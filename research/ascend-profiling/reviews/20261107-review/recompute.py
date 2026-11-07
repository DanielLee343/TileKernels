"""Recompute a read-only review inventory from committed profiling artifacts.

Use --write to create/update only this directory's inventory; --check compares
the checked-in inventory byte-for-byte with a fresh computation. No device,
Git command, profiler, capture or original case status is modified.
"""
import argparse
import base64
import collections
import csv
import hashlib
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'case-review.json'
RUNS = PROJECT / 'runs'
COLLECTOR = PROJECT / 'collector' / 'unified'
PLAN = PROJECT / 'history' / 'puma' / 'outputs' / 'tilekernels-profile-case-plan-20261106' / 'cases.json'
PARTS = ('', '3', '4', '5')
METRICS = {'ArithmeticUtilization', 'L2Cache', 'Memory', 'MemoryL0', 'MemoryUB',
           'PipeUtilization', 'ResourceConflictRatio'}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(REPO).as_posix()


def classify(group, params):
    # This classification is grounded in the listed source lines. It answers
    # only whether the captured kernel reads and writes the same input buffer.
    mapping = {
        'engram_gate_fwd': ('separate_output', 'Forward captures save=True, inplace=False; allocated outputs are separate.',
                            ['tile_kernels/engram/engram_gate_fwd_kernel.py:63',
                             'research/ascend-profiling/collector/unified/extra_engram_gate_fwd.py:101']),
        'engram_gate_bwd': ('separate_output', 'Backward allocates separate gradient outputs.',
                            ['tile_kernels/engram/engram_gate_bwd_kernel.py:71']),
        'moe_topk_gate_backward': ('separate_output', 'Backward reads inputs and writes separate grad_logits.',
                                   ['tile_kernels/moe/moe_topk_gate_backward_kernel.py:64']),
        'engram_grad_w_reduce': ('read_write_input', 'Both weight-gradient input buffers are accumulated in place.',
                                 ['tile_kernels/engram/engram_grad_w_reduce_kernel.py:16']),
        'engram_sinkhorn_momentum_update': ('read_write_input', 'The momentum buffer is read and updated in place.',
                                            ['tile_kernels/engram/engram_sinkhorn_asc.py:50']),
        'engram_sinkhorn_step': ('read_write_input', 'row_scale is read and updated in place.',
                                 ['tile_kernels/engram/engram_sinkhorn_asc.py:130',
                                  'tile_kernels/engram/engram_sinkhorn_asc.py:173']),
        'mhc_pre_apply_mix_bwd': ('read_write_input', 'x_grad is an in-place accumulated input.',
                                   ['tile_kernels/mhc/pre_apply_mix_asc.py:100',
                                    'tile_kernels/mhc/pre_apply_mix_asc.py:120']),
        'mhc_fn_normw_merge_bwd': ('read_write_input', 'fn_grad and normw_grad are accumulated in place.',
                                    ['tile_kernels/mhc/norm_fn_asc.py:112',
                                     'tile_kernels/mhc/norm_fn_asc.py:146']),
        'quant_norm_backward': ('read_write_input', 'The planned accumulate=True cases read and update weight_grad.',
                                ['tile_kernels/quant/norm_backward_asc.py:103',
                                 'tile_kernels/quant/norm_backward_asc.py:177',
                                 'tile_kernels/quant/norm_backward_asc.py:180']),
        'quant_per_token_cast_and_cast_back': ('read_write_input', 'The quantize/dequantize kernel overwrites x.',
                                               ['tile_kernels/quant/per_token_cast_and_cast_back_asc.py:376',
                                                'tile_kernels/quant/per_token_cast_and_cast_back_asc.py:383']),
        'rotary_embedding': ('read_write_input', 'Q or K is separately read and updated in place.',
                             ['tile_kernels/transform/rope_kernel.py:76',
                              'research/ascend-profiling/collector/unified/extra_rope.py:34']),
    }
    if group == 'moe_topk_gate_forward':
        if params['fix_routing']:
            return ('read_write_input', 'Fixed routing reads and writes unmapped_topk_idx.',
                    ['tile_kernels/moe/moe_topk_gate_forward_asc.py:131',
                     'tile_kernels/moe/moe_topk_gate_forward_asc.py:272'])
        return ('output_only_auxiliary_buffer', 'Without fixed routing, unmapped_topk_idx is written but not read.',
                ['tile_kernels/moe/moe_topk_gate_forward_asc.py:131',
                 'tile_kernels/moe/moe_topk_gate_forward_asc.py:272'])
    kind, reason, evidence = mapping[group]
    if group == 'quant_norm_backward' and not (params['accumulate'] and params['use_weight']):
        raise AssertionError('unexpected norm backward mode in review set')
    return kind, reason, evidence


def checked(condition, description):
    if not condition:
        raise AssertionError(description)


def build():
    groups = {g['id']: g['cases'] for g in read_json(PLAN)['groups']}
    all_cases = {}
    environments = []
    for part in PARTS:
        run = RUNS / ('hidev-20261106-unified-extra' + part)
        manifest = COLLECTOR / ('extra' + part + '_cases.json')
        env_path = run / 'environment.json'
        env = read_json(env_path)
        checked(env['manifest_sha256'] == sha(manifest), f'manifest mismatch: {run.name}')
        for name, expected in env['hooks_sha256'].items():
            checked(sha(COLLECTOR / name) == expected, f'adapter mismatch: {run.name}/{name}')
        environments.append({'run': rel(run), 'environment': rel(env_path), 'environment_sha256': sha(env_path),
                             'source_commit': env['source_commit'], 'manifest': rel(manifest),
                             'manifest_sha256': sha(manifest), 'adapter_sha256': env['hooks_sha256']})
        entries = {c['id']: c for c in read_json(manifest)['cases']}
        for result in read_json(run / 'progress.json')['cases']:
            if result['status'] != 'needs_review':
                continue
            capture_id = result['id']
            entry = entries[capture_id]
            group, number, params = entry['group'], entry['plan_case_number'], entry['params']
            checked(result['family'] == group and groups[group][number - 1] == params, f'plan mismatch: {capture_id}')
            directory = run / 'cases' / capture_id
            pre_path, post_path, result_path = (directory / n for n in ('prepare.json', 'default.json', 'result.json'))
            pre, post = read_json(pre_path), read_json(post_path)
            checked(read_json(result_path) == result, f'progress/result mismatch: {capture_id}')
            checked(result.get('prepare_rc') == result.get('default_rc') == 0, f'nonzero return: {capture_id}')
            checked(pre.get('status') == post.get('status') == 'passed' and pre.get('matched') == post.get('matched') == 1,
                    f'correctness/target mismatch: {capture_id}')
            checked(pre['inputs'] == post['inputs'] and pre['source_sha256'] == post['source_sha256']
                    and pre['runtime_kernel'] == post['runtime_kernel'], f'input/source mismatch: {capture_id}')
            for field in ('source_files_sha256', 'native_kwargs', 'native_config', 'launch_seed', 'scalar_inputs',
                          'route_counts', 'routed_scaling_factor', 'num_vec_cores', 'params', 'capture_mode',
                          'routing_fixture_inputs', 'target_role'):
                checked(pre.get(field) == post.get(field), f'{field} mismatch: {capture_id}')
            if 'params' in post:
                checked(post['params'] == params, f'recorded parameters mismatch: {capture_id}')
            command = result['default_command']
            pos = command.index('-B')
            command_params = json.loads(base64.urlsafe_b64decode(command[pos + 3].encode()))
            checked(command_params == params, f'command parameters mismatch: {capture_id}')
            checked(all(x in command for x in ('--replay-mode=kernel', '--launch-count=1', '--warm-up=5')),
                    f'profiling command mismatch: {capture_id}')
            checked(all('No process in device.' in (directory / name).read_text(encoding='utf-8')
                        for name in ('device-before.txt', 'device-after.txt')), f'idle mismatch: {capture_id}')
            checked(result.get('reason') == 'in-place profiler replay restoration has not been independently verified',
                    f'unexpected review reason: {capture_id}')
            files = result['capture']['files']
            checked(set(files) == METRICS | {'OpBasicInfo'}, f'metric set mismatch: {capture_id}')
            metric_files = {}
            for name, info in files.items():
                path = run / info['path']
                checked(sha(path) == info['sha256'], f'metric sha mismatch: {capture_id}/{name}')
                metric_files[name] = {'path': rel(path), 'sha256': info['sha256']}
            with (run / files['OpBasicInfo']['path']).open(encoding='utf-8-sig', newline='') as source:
                rows = list(csv.DictReader(source))
            checked(len(rows) == 1 and rows[0]['Op Name'] == pre['runtime_kernel'] and rows[0]['Device Id'] == '0'
                    and rows[0]['Op Type'] == 'vector', f'OpBasicInfo mismatch: {capture_id}')
            blocks = int(rows[0]['Block Dim'])
            checked(blocks == 56, f'unexpected block dim: {capture_id}')
            for name in METRICS:
                with (run / files[name]['path']).open(encoding='utf-8-sig', newline='') as source:
                    metric_rows = list(csv.DictReader(source))
                checked(len(metric_rows) == blocks and {(x['block_id'], x['sub_block_id']) for x in metric_rows}
                        == {(str(i), 'vector0') for i in range(blocks)}, f'metric rows: {capture_id}/{name}')
            if group == 'moe_topk_gate_backward':
                checked(post['captured_fix_routing'] == params['fix_routing'], f'routing mismatch: {capture_id}')
            if group == 'engram_gate_fwd':
                checked(post['capture_mode'] == {'save_for_backward': True, 'inplace': False}, f'mode: {capture_id}')
            role = post.get('target_role') if group == 'rotary_embedding' else None
            if group == 'rotary_embedding':
                checked(role in ('query', 'key') and capture_id.endswith('-' + ('q' if role == 'query' else 'k')),
                        f'RoPE role mismatch: {capture_id}')
            kind, reason, evidence = classify(group, params)
            case_id = f'{group}-{number:02d}'
            disposition = 'inplace_restoration_review_not_applicable' if kind != 'read_write_input' else 'retain_inplace_restoration_review'
            case = all_cases.setdefault(case_id, {'case_id': case_id, 'family': group, 'plan_case_number': number,
                                                  'params': params, 'buffer_class': kind, 'classification_reason': reason,
                                                  'source_evidence': evidence, 'review_disposition': disposition,
                                                  'captures': []})
            checked(case['params'] == params and case['buffer_class'] == kind, f'case collision: {case_id}')
            capture = {'capture_id': capture_id, 'target_role': role, 'original_status': result['status'],
                       'original_reason': result['reason'], 'prepare': rel(pre_path), 'prepare_sha256': sha(pre_path),
                       'default': rel(post_path), 'default_sha256': sha(post_path), 'result': rel(result_path),
                       'result_sha256': sha(result_path), 'kernel': post['runtime_kernel'],
                       'generated_source_sha256': post['source_sha256'], 'block_dim': blocks,
                       'route_counts': post.get('route_counts'), 'metric_files': metric_files,
                       'checks': {'original_plan_and_command_match': True, 'upstream_stage_status_passed': True,
                                  'one_marked_target': True, 'prepare_default_input_source_match': True,
                                  'device_idle_records_passed': True, 'metric_hash_and_rows_match': True,
                                  'kernel_replay_launch1_warmup5_recorded': True}}
            case['captures'].append(capture)
    cases = sorted(all_cases.values(), key=lambda x: (x['family'], x['plan_case_number']))
    checked(len(cases) == 220 and sum(len(c['captures']) for c in cases) == 240, 'unexpected inventory size')
    for case in cases:
        roles = {x['target_role'] for x in case['captures']}
        checked((len(case['captures']) == 2 and roles == {'query', 'key'}) if case['family'] == 'rotary_embedding'
                else len(case['captures']) == 1, f'capture mapping: {case["case_id"]}')
    case_counts = collections.Counter(c['review_disposition'] for c in cases)
    capture_counts = collections.Counter(c['review_disposition'] for c in cases for _ in c['captures'])
    checked(case_counts == {'inplace_restoration_review_not_applicable': 70,
                            'retain_inplace_restoration_review': 150}, 'unexpected case classification')
    checked(capture_counts == {'inplace_restoration_review_not_applicable': 70,
                               'retain_inplace_restoration_review': 170}, 'unexpected capture classification')
    return {'scope': '220 original plan cases, 240 native captures previously marked needs_review',
            'limitations': ['No original result status was changed.',
                            'Non-applicable refers only to the in-place restoration reason, not all profiler semantics.',
                            'Passed final correctness does not independently establish restoration of mutable inputs during each profiler replay.',
                            'The Q/K captures are separate native kernels, not a fused RoPE result.',
                            'Gate forward profiles only save_for_backward=True, inplace=False.',
                            'MoE forward fixed-routing fixture suppresses force_random; record actual route_counts.',
                            'No NPU run or physical performance validation was performed by this review.'],
            'original_plan': rel(PLAN), 'original_plan_sha256': sha(PLAN), 'environment_bindings': environments,
            'case_counts': dict(sorted(case_counts.items())), 'capture_counts': dict(sorted(capture_counts.items())),
            'cases': cases}


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    if args.write:
        OUT.write_text(rendered, encoding='utf-8', newline='\n')
    else:
        checked(OUT.read_text(encoding='utf-8') == rendered, 'stored inventory differs from recomputation')
    print('PASS: 220 plan cases, 240 captures, 70 non-applicable and 150 retained; mode=' + ('write' if args.write else 'check'))


if __name__ == '__main__':
    main()
