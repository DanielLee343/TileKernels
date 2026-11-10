"""Assemble the frozen target ledger and profile windows into typed sheet rows."""

import argparse
import gzip
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

from profile_rows import DERIVED, audit_requested, derive, load_window, numeric, read_csv
from restore_bundles import long_path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BACKFILL = ROOT / 'outputs/expert-profile-backfill-20261109'
ARCHIVE = ROOT / 'outputs/expert-profile-inventory-20261109'
RECAP = ROOT / 'outputs/gcm-profile-screen-20261108/mte3-x1-x3'
TYPES = {'vector': 'Vector', 'cube': 'Cube', 'mix': 'CV融合'}
META = ['目标 ID', 'Case', '目标 kernel', '记录粒度', '窗口序号', '核侧', 'block_id',
        'sub_block_id', '目标覆盖状态', '记录状态', '设备', '设备健康', '采集模式',
        '任务耗时 (µs)', 'Block Dim', 'Mix Block Dim', '当前频率 (MHz)', '额定频率 (MHz)',
        '原始 Op Name', '数据集', '输入和配置', '复算状态', '采集来源', '对账证据',
        '原始 Op Type', '原始 Device Id', '原始 Pid']
LABELS = {
    'pending': '逐核搬出待核', 'blocked_32_cube_required': '固定上游版本不兼容 28 核设备',
    'aiv_not_applicable': '无 Vector 侧', 'aiv_ub_to_gm_not_applicable': 'UB→GM 不适用',
    'existing_dbi_audited': '搬出请求字节已对账', 'new_dbi_audited': '搬出请求字节已对账',
    'new_dbi_audited_alarm': '搬出请求字节已对账，设备告警',
    'dbi_window_coverage_verified_traffic_unverified': '地址覆盖已核对，总搬运待核',
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def mirror_detail(suffix, entry):
    mirrors = [Path(p) for p in os.environ.get('PUMA_HIDEV_RAW_ROOTS', '').split(os.pathsep) if p]
    cache_index = HERE / 'archive-mirrors.json'
    if cache_index.is_file():
        mirrors.extend(Path(p) for p in read_json(cache_index))
    mirrors.append(BACKFILL / 'hidev-evidence')
    for root in reversed(mirrors):
        root = long_path(root.resolve())
        detail = root / suffix
        if not detail.is_dir():
            continue
        checks = entry.get('files_sha256', {})
        matches = True
        for relative, digest in checks.items():
            file = root / relative
            if not file.is_file():
                matches = False
                break
            with file.open('rb') as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
                    matches = False
                    break
        if matches:
            return detail
    return None


def file_reference(path):
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def label(target):
    state = target['per_core_requested_bytes_status']
    return LABELS.get(state, state)


def original_role(target):
    if target['batch'] == 'tilekernels-precision':
        result = target['original_evidence']
        return '历史 CPU 参考失败' if result == 'mismatch' else '历史 CPU 参考失败；NPU 分块对照通过'
    if target['batch'] == 'deepgemm-experimental':
        return '28 核适配实验'
    if target['batch'] == 'tilekernels-default' and target['original_evidence'] not in ('admitted', 'passed'):
        return '历史标签：' + target['original_evidence']
    return '已存档'


def parse_value(field, value):
    if value in (None, ''):
        return None
    if value == 'NA':
        return 'NA'
    number = numeric(value)
    if number is None:
        return value
    if re.fullmatch(r'-?\d+', str(value)):
        return int(value)
    return number


def window_mode(detail, fallback):
    command = detail / 'command.json'
    if not command.is_file():
        return fallback, False
    args = read_json(command)
    if isinstance(args, dict):
        args = args.get('command') or args.get('argv') or []
    if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
        return fallback, False
    metrics = next((arg.split('=', 1)[1] for arg in args if arg.startswith('--aic-metrics=')), fallback)
    replay = next((arg.split('=', 1)[1] for arg in args if arg.startswith('--replay-mode=')), '')
    return metrics + (f' / {replay} replay' if replay else ''), 'kernelscale' in metrics.lower()


def enrich(folder, basic, rows, audit, kernel_scale):
    log = folder / 'profile.log'
    if not audit:
        return {}, '无逐核地址对账'
    op_text = '\n'.join(x.read_text(errors='replace') for x in folder.rglob('op_basic_info.txt'))
    if 'Run Soc Version=Ascend950PR_9579' not in op_text or kernel_scale:
        return {}, 'SoC 或原始时间口径未验证'
    if not log.is_file():
        return {}, '同窗日志缺失'
    try:
        return derive(basic, rows, log, audit), '四列已按同窗复算'
    except (ValueError, KeyError, ZeroDivisionError) as exc:
        return {}, str(exc)


def window(target, path, mode, device, health, evidence='', audit=None, basic_path=None, role=None):
    basic, rows = load_window(path, basic_path)
    if basic['Op Type'] != target['op_type'] or basic['Op Name'] != target['op_name']:
        raise ValueError(f"kernel identity mismatch for {target['target_id']} at {path}")
    path = Path(path)
    # The raw log is alongside the capture directory rather than inside OPPROF.
    detail = path.parent.parent if path.parent.name == 'capture' else path
    mode, kernel_scale = window_mode(detail, mode)
    if audit and audit.get('status') == 'aiv_ub_to_gm_not_applicable':
        derivation, why = {}, '新窗口无 UB→GM；SIMT 直接写主存，历史二进制未保留'
    else:
        derivation, why = enrich(detail, basic, rows, audit, kernel_scale)
    if audit and not derivation:
        requested = audit_requested(audit)
        for block, subblock in rows:
            if subblock.startswith('vector'):
                flat = (block * 2 + int(subblock.removeprefix('vector'))
                        if basic['Op Type'] == 'mix' else block)
                if flat in requested:
                    derivation[block, subblock] = [requested[flat], None, None, None, None, None]
    return dict(target=target['target_id'], mode=mode, device=device, health=health,
                source=file_reference(Path(path)), evidence=evidence,
                role=role or original_role(target), basic=basic, why=why,
                rows=[[block, subblock, values, derivation.get((block, subblock))]
                      for (block, subblock), values in sorted(rows.items())])


def accepted_original(row):
    return row['batch'] == 'deepgemm-original' or row['evidence'] in {
        'admitted', 'passed_chunked_comparison', 'warmup5_single_kernel', 'warmup5_QK_range',
    }


def raw_windows(target, archived, tbe_new, hidev_new, deep_new, extra, mega_partial,
                accepted_only):
    target_id = target['target_id']
    for path in filter(None, target['original_opbasic_csv'].split(';')):
        p = ROOT / path
        row = archived[file_reference(p.parent)]
        if accepted_only and not accepted_original(row):
            continue
        device = '历史归档'
        if row['batch'] == 'tilekernels-default':
            device = 'HiDev 950PR 57:00.0'
        mode = row['mode'] + (' / range replay' if 'range' in row['evidence'] else '')
        yield window(target, p.parent, mode, device, '历史状态按来源', basic_path=p)

    for row in extra.get(target_id, []):
        path = ROOT / row['profile_path']
        if row['batch'] == 'tbe-mhc' and row['mode'] == 'MemoryDetail+DEBUG':
            audit_path = path.parents[2] / 'audit-final.json'
        elif row['batch'] == 'tbe-swiglu-smoke':
            audit_path = RECAP / 'byte-smoke/tbe/dbi-address-audit.json'
        else:
            audit_path = None
        yield window(target, path, row['mode'], 'tbe 950PR 卡 4', '见采集记录',
                     file_reference(audit_path) if audit_path else '',
                     read_json(audit_path) if audit_path else None, role='独立复采')

    new = tbe_new.get(target_id)
    if new:
        suffix = new['remote_detail'].split('/runs/', 1)[1]
        base = BACKFILL / 'tbe-evidence'
        detail = next((d for d in (base / 'runs' / suffix, base / 'batch-reduce-02-13/runs' / suffix)
                       if d.is_dir()), None)
        if detail:
            basic, = detail.rglob('OpBasicInfo.csv')
            yield window(target, basic.parent, 'MemoryDetail,Default', new['device'], '见采集记录',
                         new['audit'], read_json(ROOT / new['audit']), role='独立复采')

    new = hidev_new.get(target_id) or deep_new.get(target_id)
    if new:
        suffix = new['remote_detail'].split('/expert-profile-backfill-20261109-hidev/', 1)[1]
        detail = mirror_detail(suffix, new)
        if detail:
            basic, = detail.rglob('OpBasicInfo.csv')
            role = ('28 核独立实现，历史对照更快' if target_id == 'fused-h3584' else '新窗口 UB→GM 不适用，SIMT 写主存' if target_id.startswith('head-fp32-') and target['batch']=='tilekernels-earlier' else '独立复采，设备告警')
            record = window(target, basic.parent, 'MemoryDetail,Default', new['device'], new['health'],
                            new['audit'], read_json(ROOT / new['audit']), role=role)
            record['source'] = new['remote_detail']
            yield record
        else:
            yield dict(target=target_id, mode='MemoryDetail,Default', device=new['device'],
                       health=new['health'], source=new['remote_detail'], evidence=new['audit'],
                       role='逐核请求已对账，原始表待取回', basic={}, rows=[],
                       why='需同一窗口原始表和日志')
    if target_id in mega_partial:
        entry = mega_partial[target_id]
        yield dict(target=target_id, mode='MemoryDetail / application replay', device='HiDev NPU 0',
                   health=entry['health'], source=entry['raw_dir'],
                   evidence='outputs/expert-profile-backfill-20261109/mega28-dbi-index.json',
                   role='28 核适配，独立 DBI 轮通过正确性', basic={}, rows=[],
                   why='预期地址已覆盖，总搬运完整性和同轮 PMU 待核')


def row_values(target, window, fields, block=None, subblock=None, original=None, derived=None):
    basic = window['basic']
    grain = '采集' if block is None else '逐核'
    side = (None if subblock is None else 'AIV' if subblock.startswith('vector') else 'AIC')
    reason = window['why']
    if derived and derived[1] is not None and derived[4] is None:
        reason = 'MTE3 活跃时间为零或缺失，活跃带宽无值'
    case = target['case'].split('/', 1)[-1] if target['batch'].startswith('deepgemm-') else target['case']
    case_meta = [target['target_id'], case, target['kernel_label'], grain, window['window_id'],
                 side, block, subblock, label(target), window['role'], window['device'], window['health'],
                 window['mode'], parse_value('', basic.get('Task Duration(us)')) if block is None else None,
                 parse_value('', basic.get('Block Dim')), parse_value('', basic.get('Mix Block Dim')),
                 parse_value('', basic.get('Current Freq')), parse_value('', basic.get('Rated Freq')),
                 basic.get('Op Name'), target['batch'], target['input_spec'] if block is None else None,
                 reason, window['source'], window['evidence'], basic.get('Op Type'),
                 parse_value('', basic.get('Device Id')), parse_value('', basic.get('Pid'))]
    return case_meta + [parse_value(f, (original or {}).get(f)) for f in fields] + list(derived or [None] * len(DERIVED))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--accepted-snapshot', type=Path)
    parser.add_argument('--output-dir', type=Path, default=HERE)
    args = parser.parse_args()
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    accepted_only = args.accepted_snapshot is not None
    indexes = args.accepted_snapshot if accepted_only else BACKFILL
    ledger = read_csv(indexes / 'targets.csv')
    assert len({r['target_id'] for r in ledger}) == len(ledger)
    arch = read_csv(ARCHIVE / 'captures.csv')
    archived = {r['profile_path']: r for r in arch}
    extra = defaultdict(list)
    for row in arch:
        if row['batch'] in ('tbe-mhc', 'tbe-swiglu-smoke'):
            extra[row['target_id']].append(row)
    tbe = read_json(indexes / 'new-captures.json')
    hidev = read_json(indexes / 'new-captures-hidev.json')
    deep = read_json(indexes / 'deepgemm-new-captures.json')
    if accepted_only:
        # Capture indexes also retain attempts whose acceptance was later withdrawn.
        audited = {r['target_id']: {r['remote_detail_path'], r['secondary_detail_path']}
                   for r in ledger if r['per_core_requested_bytes_status'] in
                   ('new_dbi_audited', 'new_dbi_audited_alarm', 'aiv_ub_to_gm_not_applicable')}
        tbe, hidev, deep = (
            {k: entry for k, entry in records.items()
             if entry['remote_detail'] in audited.get(k, set())}
            for records in (tbe, hidev, deep)
        )
    mega_index = BACKFILL / 'mega28-dbi-index.json'
    mega_partial = ({'mega-port28-experiment/' + x['case']: x for x in read_json(mega_index)['cases']}
                    if not accepted_only and mega_index.is_file() else {})
    dg_archive = read_json(ROOT / 'outputs/cube-rule02-deepgemm-20261107/audit.json')
    dg_labels = {f"{r['campaign']}/{r['id']}": r['target']
                 for r in dg_archive['cases'] + dg_archive['experimental']}
    for target in ledger:
        target['kernel_label'] = dg_labels.get(target['target_id'], target['op_name'])
    catalog = read_csv(ARCHIVE / 'metric-catalog.csv')
    remote = defaultdict(dict)
    source_file = HERE / 'hidev-windows.jsonl.gz'
    if source_file.is_file() and not accepted_only:
        with gzip.open(source_file, 'rt', encoding='utf-8') as f:
            for line in f:
                w = json.loads(line)
                if w['source'] in remote[w['target']]:
                    raise ValueError(f"duplicate exported window {w['source']}")
                remote[w['target']][w['source']] = w
    counts = {}
    included_targets = {}
    unavailable_accepted = []
    for kind, sheet in TYPES.items():
        wanted = {'vector': {'aiv', 'aic+aiv'}, 'cube': {'aic', 'aic+aiv'},
                  'mix': {'aic', 'aiv', 'aic+aiv'}}[kind]
        fields = [x['field'] for x in catalog if x['scope'] in wanted]
        stats = Counter()
        with (output / f'{kind}.jsonl').open('w', encoding='utf-8') as handle:
            handle.write(json.dumps(META + fields + list(DERIVED), ensure_ascii=False) + '\n')
            for target in (x for x in ledger if x['op_type'] == kind):
                items = list(raw_windows(target, archived, tbe, hidev, deep, extra, mega_partial,
                                         accepted_only))
                imported = remote.pop(target['target_id'], {})
                for w in imported.values():
                    if w['basic']['Op Type'] != kind or w['basic']['Op Name'] != target['op_name']:
                        raise ValueError(f"exported window identity mismatch {w['source']}")
                items = [w for w in items if w['source'] not in imported] + list(imported.values())
                if accepted_only:
                    for w in items:
                        if not w['rows']:
                            unavailable_accepted.append({'target': target['target_id'],
                                                         'source': w['source'], 'reason': w['why']})
                    items = [w for w in items if w['rows']]
                    if not items:
                        continue
                if not items:
                    items = [dict(basic={}, rows=[], mode='', device='', health='', source='', evidence='',
                                  role=label(target), why='缺整份原版采集')]
                assert len({w['source'] for w in items}) == len(items), target['target_id']
                stats['targets'] += 1
                stats['target_status_' + target['per_core_requested_bytes_status']] += 1
                included_targets[target['target_id']] = len(items)
                for ix, w in enumerate(items, start=1):
                    w['window_id'] = ix
                    stats['window_rows'] += 1
                    if not w['rows']:
                        stats['window_without_raw_rows'] += 1
                    elif w['why'] == '四列已按同窗复算':
                        stats['windows_recomputed'] += 1
                    rows = [row_values(target, w, fields)]
                    for block, subblock, original, derived in w['rows']:
                        stats['core_rows'] += 1
                        stats['core_role_' + ('aiv' if subblock.startswith('vector') else 'aic')] += 1
                        rows.append(row_values(target, w, fields, block, subblock, original, derived))
                    for row in rows:
                        handle.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        counts[kind] = dict(stats, sheet=sheet, columns=len(META) + len(fields) + len(DERIVED))
    assert not remote, sorted(remote)
    assert sum(r['targets'] for r in counts.values()) == len(included_targets)
    if not accepted_only:
        assert len(included_targets) == len(ledger)
    snapshot = {'accepted_only': accepted_only, 'targets': included_targets,
                'unavailable_accepted': unavailable_accepted}
    (output / 'export-scope.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2),
                                            encoding='utf-8')
    (output / 'counts.json').write_text(json.dumps(counts, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(counts, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
