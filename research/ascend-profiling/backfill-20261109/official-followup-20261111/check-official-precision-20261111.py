"""Diagnose the original precision failures with a separate FP64 reference."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path


def load_script(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_stats(stats, actual, expected, atol, rtol):
    error = (actual.detach().double() - expected.detach().double()).abs()
    assert error.isfinite().all()
    stats['over_tolerance'] += int((error > atol + rtol * expected.double().abs()).sum())
    stats['max_abs'] = max(stats['max_abs'], float(error.max()))
    stats['elements'] += actual.numel()


def stats():
    return {'over_tolerance': 0, 'max_abs': 0.0, 'elements': 0}


def normalize(item, root, torch):
    module = load_script(root / 'precision-normalize03-harness-20261110/collector_starter.py')
    kernel, host, device, old_ref = module.build(item['case'], torch)
    assert [module.describe(x, True) for x in host] == item['expected_inputs']
    actual = [torch.empty_like(x, device='npu:0') for x in old_ref]
    kernel(*device, *actual)
    torch.npu.synchronize()
    source = kernel.get_kernel_source().encode()
    sha = hashlib.sha256(source).hexdigest()
    prior_path = rb'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/'
    this_path = rb'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/'
    assert sha == item['expected_source_sha256'] or hashlib.sha256(source.replace(this_path, prior_path)).hexdigest() == item['expected_source_sha256']
    inputs, = host
    exact = inputs.double().sum(-1) + 1e-20
    new_ref = (exact, inputs.double() / exact[:, None])
    result = {}
    for tag, reference in [('original_cpu', old_ref), ('fp64', new_ref)]:
        result[tag] = [stats(), stats()]
        for got, ref, entry in zip(actual, reference, result[tag], strict=True):
            add_stats(entry, got.cpu(), ref, 2e-6, 0)
    return {'input_and_source_match': True, 'source_sha256': sha, 'comparisons': result}


def preapply(item, root, out, torch):
    module = load_script(root / 'extra-proxy-mhc-pre-apply-bwd-app-harness/extra_mhc_pre_apply_bwd.py')
    result = {tag: [stats(), stats()] for tag in ('original_cpu', 'fused_fp64', 'fp64_dx_before_rounding')}

    def compare(x, mix, dy, initial, dx, dmix, reference, torch):
        for start in range(0, x.shape[0], 64):
            span = slice(start, start + 64)
            rx = x[span].cpu().float().unsqueeze(0).requires_grad_()
            rm = mix[span].cpu().unsqueeze(0).unsqueeze(-1).requires_grad_()
            grad = dy[span].cpu().unsqueeze(0)
            original = initial[span].cpu().unsqueeze(0)
            gx, gm = torch.autograd.grad(reference(rx, rm), (rx, rm), grad)
            actual = dx[span].cpu().unsqueeze(0), dmix[span].cpu().unsqueeze(0)
            precise_dx = original.double() + grad.double().unsqueeze(2) * rm.double()
            precise_mix = (rx.double() * grad.double().unsqueeze(2)).sum(-1)
            checks = {
                'original_cpu': ((original.float() + gx).bfloat16(), gm.squeeze(-1)),
                'fused_fp64': (precise_dx.float().bfloat16(), precise_mix),
                'fp64_dx_before_rounding': (precise_dx, precise_mix),
            }
            for tag, expected in checks.items():
                for got, ref, entry in zip(actual, expected, result[tag], strict=True):
                    add_stats(entry, got, ref, 1e-2, 1e-3)
        return []

    module.verify_outputs = compare
    invocation_dir = out / item['id']
    invocation_dir.mkdir()
    record = invocation_dir / f'application-{os.getpid()}.json'
    module.run(item['family'], item['params'], 'prepare', record)
    actual = json.loads(record.read_text())
    assert actual['inputs'] == item['expected_inputs']
    assert actual['source_sha256'] == item['expected_source_sha256']
    return {'input_and_source_match': True, 'source_sha256': actual['source_sha256'], 'comparisons': result}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive', type=Path)
    p.add_argument('backfill', type=Path)
    p.add_argument('out', type=Path)
    p.add_argument('ids', nargs='+')
    args = p.parse_args()
    import torch
    import torch_npu  # noqa: F401 -- registers device support

    torch.set_num_threads(8)
    torch.npu.set_device(0)
    plan = json.loads((args.archive / 'accuracy-plan.json').read_text())
    cases = {item['id']: item for item in plan['cases']}
    for key in args.ids:
        item = cases[key]
        if item['family'] == 'moe_normalize_weight':
            verdict = normalize(item, args.backfill, torch)
        else:
            assert item['family'] == 'mhc_pre_apply_mix_bwd'
            verdict = preapply(item, args.backfill, args.out, torch)
        (args.out / f'{key}-fp64-reference.json').write_text(json.dumps(verdict, indent=2) + '\n')
        print(key, json.dumps(verdict), flush=True)


if __name__ == '__main__':
    main()
