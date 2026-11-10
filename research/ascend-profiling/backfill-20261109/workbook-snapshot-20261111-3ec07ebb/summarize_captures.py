"""Produce one row per capture and check source field coverage by target."""

import argparse
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from itertools import groupby
from pathlib import Path

from prepare_workbook import ARCHIVE
from profile_rows import DERIVED


BASE = ['目标 ID', 'Case', '目标 kernel', '窗口序号', '任务耗时 (µs)', '设备',
        '设备健康', '采集模式', 'Block Dim', 'Mix Block Dim', '数据集', '目标覆盖状态', '记录状态',
        '向量核搬出状态', '复算状态', '输入和配置', '采集来源', '对账证据']
MOVE = ['AIV 向量核搬出请求量 (B)\nΣ(各核请求字节)',
        'AIV 工具计入 UB 侧字节 (B)\nΣ(各核 UB 侧计量)',
        'AIV 搬出任务带宽 (GiB/s)\nΣ(UB 侧 B)×10⁶ ÷ (2³⁰×任务µs)',
        'AIV 搬出活跃带宽 (GiB/s)\nΣ(UB 侧 B)×10⁶ ÷ (2³⁰×Σ活动µs)']
BYTES = {'AIV': ('GM_to_UB_datas(KB)',),
         'AIC': ('GM_to_L1_datas(KB)', 'L0C_to_GM_datas(KB)', 'L0C_to_L1_datas(KB)')}
PIPES = {'AIV': ('vec', 'scalar', 'mte2', 'mte3'),
         'AIC': ('cube', 'scalar', 'mte1', 'mte2', 'mte3', 'fixpipe')}
RATIOS = {'AIV': (*PIPES['AIV'], 'vec_vf', 'vec_sfu', 'vec_simt_vf', 'vec_sfu_cflt',
                  'vec_ldu_cflt', 'vec_stu_cflt', 'vec_wait', 'mte2_wait', 'mte3_wait'),
          'AIC': (*PIPES['AIC'], 'cube_fp', 'cube_int', 'cube_wait', 'mte1_wait',
                  'mte2_wait', 'mte3_wait')}
INSTRUCTIONS = {'AIV': ('mte2_instructions', 'mte3_instructions'),
                'AIC': ('cube_total_instr_number', 'cube_fp_instr_number',
                        'cube_int_instr_number', 'mte1_instructions', 'mte2_instructions',
                        'mte3_instructions')}
DIRECT_BW = {
    'AIV': (('GM→UB 向量核搬入', 'GM_to_UB_datas(KB)'),
            ('主存读', 'read_main_memory_datas(KB)'), ('主存写', 'write_main_memory_datas(KB)')),
    'AIC': (('GM→L1 搬入', 'GM_to_L1_datas(KB)'), ('L0C→GM', 'L0C_to_GM_datas(KB)'),
            ('L0C→L1', 'L0C_to_L1_datas(KB)'), ('主存读', 'read_main_memory_datas(KB)'),
            ('主存写', 'write_main_memory_datas(KB)')),
}
RATE_ONLY_BW = {
    'AIV': (('UB→Vector', 'ub_read_bw_vector'), ('Vector→UB', 'ub_write_bw_vector')),
    'AIC': (('L1 读', 'l1_read_bw'), ('L1 写', 'l1_write_bw'),
            ('L0A 读', 'l0a_read_bw'), ('L0A 写', 'l0a_write_bw'),
            ('L0B 读', 'l0b_read_bw'), ('L0B 写', 'l0b_write_bw'),
            ('L0C→Cube', 'l0c_read_bw_cube'), ('Cube→L0C', 'l0c_write_bw_cube')),
}
KB_RATE = 10**6 / 2**20
BYTE_RATE = 10**6 / 2**30
ROLES = {'vector': ('AIV',), 'cube': ('AIC',), 'mix': ('AIC', 'AIV')}
UB_FIELDS = ('UB_to_GM_datas(KB)', 'UB_to_GM_bw_usage_rate(%)',
             'aiv_mte3_active_bw(GB/s)', 'aiv_ub_read_bw_gm(GB/s)', 'aiv_ub_to_gm_bw(GB/s)')


def finite(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def complete(values):
    return bool(values) and all(finite(v) for v in values)


def total(values):
    return sum(values) if complete(values) else None


def maximum(values):
    return max(values) if complete(values) else None


def ratio(num, den, scale=1):
    return scale * num / den if finite(num) and finite(den) and den > 0 else None


def sum_products(values, weights):
    if complete(values) and complete(weights):
        return sum(v * w for v, w in zip(values, weights, strict=True))
    return None


def role_fields(role):
    p = role.lower()
    entries = [(f'{role} 逐核记录数\n核侧行数', None, 'count'),
               (f'{role} 最慢核耗时 (µs)\nmax(核耗时)', f'{p}_time(us)', 'max'),
               (f'{role} 核周期合计\nΣ(核周期)', f'{p}_total_cycles', 'sum')]
    entries += [(f'{role} {field}\nΣ(各核计量)', field, 'sum')
                for field in (*BYTES[role], 'read_main_memory_datas(KB)', 'write_main_memory_datas(KB)')]
    entries += [(f'{role} {pipe} 活动时间 (核·µs)\nΣ(各核活动时间)', f'{p}_{pipe}_time(us)', 'sum')
                for pipe in PIPES[role]]
    entries += [(f'{role} {field}\nΣ(各核指令数)', f'{p}_{field}', 'sum') for field in INSTRUCTIONS[role]]
    entries += [(f'{role} {metric}_ratio (0–1)\nΣ(核比率×核周期) ÷ Σ(核周期)',
                 f'{p}_{metric}_ratio', 'weighted')
                for metric in RATIOS[role]]
    for direction in ('read', 'write'):
        entries += [(f'{role} L2 {direction}_{distance}_{event}\nΣ(各核计数)',
                     f'{p}_{direction}_{distance}_{event}', 'sum')
                    for distance in ('close', 'far') for event in ('hit', 'miss', 'victim')]
        entries.append((f'{role} L2 {direction} 命中率 (%)\n100×Σhit ÷ Σ(hit+miss+victim)',
                        direction, 'l2'))
    entries += [(f'{role} {name} 任务带宽 (GiB/s)\nΣ(KiB)×10⁶ ÷ (2²⁰×任务µs)',
                 field, 'task_bw') for name, field in DIRECT_BW[role]]
    entries += [(f'{role} {name} 任务带宽 (GiB/s，约)\nΣ(核带宽×原分母) ÷ 任务µs',
                 f'{p}_{field}(GB/s)', 'tool_bw') for name, field in RATE_ONLY_BW[role]]
    entries += [(f'{role} MTE2 活跃带宽 (GiB/s)\nΣ(搬入 KiB)×10⁶ ÷ (2²⁰×Σ活动µs)',
                 BYTES[role][0], 'mte2_bw')]
    if role == 'AIC':
        entries += [(f'{role} {pipe} 活跃带宽 (GiB/s，约)\nΣ(核带宽×活动µs) ÷ Σ活动µs',
                     pipe.lower(), 'active_bw') for pipe in ('MTE1', 'MTE3', 'FixPipe')]
    return entries


def get_values(rows, field):
    return [r.get(field) for r in rows]


def l2_hit_rate(rows, prefix, direction):
    counts = {event: total([r.get(f'{prefix}_{direction}_{distance}_{event}') for r in rows
                            for distance in ('close', 'far')])
              for event in ('hit', 'miss', 'victim')}
    return ratio(counts['hit'], total(list(counts.values())), 100)


def summarize_role(role, rows, capture):
    prefix = role.lower()
    cycles = get_values(rows, f'{prefix}_total_cycles')
    task_time = capture['任务耗时 (µs)']
    # On the 950PR the tool uses task time for mixed captures, and core time
    # for pure AIC/AIV captures. KernelScale uses a separate scope.
    mode = (capture['采集模式'] or '').lower()
    raw_duration = ([task_time] * len(rows) if capture['原始 Op Type'] == 'mix'
                    else get_values(rows, f'{prefix}_time(us)'))
    if 'kernelscale' in mode or not all(finite(t) and t > 0 for t in raw_duration):
        raw_duration = []
    values = []
    for _, field, method in role_fields(role):
        items = get_values(rows, field)
        if method == 'count':
            value = len(rows)
        elif method == 'max':
            value = maximum(items)
        elif method == 'sum':
            value = total(items)
        elif method == 'weighted':
            value = ratio(sum_products(items, cycles), total(cycles))
        elif method == 'l2':
            value = l2_hit_rate(rows, prefix, field)
        elif method == 'task_bw':
            value = ratio(total(items), task_time, KB_RATE)
        elif method == 'tool_bw':
            value = ratio(sum_products(items, raw_duration), task_time)
        elif method == 'mte2_bw':
            value = ratio(total(items), total(get_values(rows, f'{prefix}_mte2_time(us)')), KB_RATE)
        elif method == 'active_bw':
            active_time = get_values(rows, f'{prefix}_{field}_time(us)')
            bandwidth = get_values(rows, f'{prefix}_{field}_active_bw(GB/s)')
            numer = sum_products(bandwidth, active_time) if all(
                finite(t) and t > 0 for t in active_time) else None
            value = ratio(numer, total(active_time))
        else:
            raise ValueError(f'Unknown aggregation method {method}')
        values.append(value)
    return values


def movement(capture, rows):
    data = [total(get_values(rows, f)) for f in DERIVED[:2]]
    if complete(data):
        label = '该次采集已对账'
    elif not rows or capture['目标覆盖状态'] == 'UB→GM 不适用':
        label = '不适用'
    elif capture['目标覆盖状态'].startswith('搬出请求字节已对账'):
        label = '本次无值，目标另有已对账采集'
    else:
        label = '本次缺逐核搬出对账'
    return label, data + [
        ratio(data[1], capture['任务耗时 (µs)'], BYTE_RATE),
        ratio(data[1], total(get_values(rows, 'aiv_mte3_time(us)')), BYTE_RATE),
    ]


def iter_windows(path):
    with path.open(encoding='utf-8') as source:
        headers = json.loads(next(source))
        def by_window(row):
            return row[0], row[4]
        for key, group in groupby(map(json.loads, source), key=by_window):
            rows = [dict(zip(headers, row, strict=True)) for row in group]
            capture, *cores = rows
            assert capture['记录粒度'] == '采集' and cores, key
            assert all(row['记录粒度'] == '逐核' for row in cores), key
            yield key, capture, cores


def field_coverage(capture, role, rows, fields, observed, filled):
    if not rows:
        return
    no_ub = capture['目标覆盖状态'] == 'UB→GM 不适用'
    for field in fields:
        if role == 'AIV' and field in UB_FIELDS and no_ub:
            continue
        label = f'{role} {field}'
        observed.add(label)
        if complete(get_values(rows, field)):
            filled.add(label)
    if role == 'AIV' and not no_ub:
        for field in DERIVED:
            label = f'AIV {field}'
            observed.add(label)
            if complete(get_values(rows, field)):
                filled.add(label)


def main(folder, output):
    with (ARCHIVE / 'metric-catalog.csv').open(encoding='utf-8-sig') as source:
        catalog = list(csv.DictReader(source))
    fields = {role: [r['field'] for r in catalog if r['scope'] in (role.lower(), 'aic+aiv')]
              for role in ('AIC', 'AIV')}
    audit = defaultdict(lambda: (set(), set()))
    counts = {}
    by_move = {}
    for kind, roles in ROLES.items():
        by_move[kind] = Counter()
        with (output / f'{kind}-capture.jsonl').open('w', encoding='utf-8') as out:
            headers = BASE + [name for role in roles for name, _, _ in role_fields(role)]
            if 'AIV' in roles:
                headers += MOVE
            out.write(json.dumps(headers, ensure_ascii=False) + '\n')
            for key, capture, cores in iter_windows(folder / f'{kind}.jsonl'):
                by_role = {role: [row for row in cores if row['核侧'] == role] for role in roles}
                label, moved = movement(capture, by_role.get('AIV', []))
                by_move[kind][label] += 1
                capture['向量核搬出状态'] = label
                row = [capture[field] for field in BASE]
                for role, core_rows in by_role.items():
                    row.extend(summarize_role(role, core_rows, capture))
                    field_coverage(capture, role, core_rows, fields[role], *audit[key[0]])
                if 'AIV' in roles:
                    row.extend(moved)
                assert len(headers) == len(row)
                out.write(json.dumps(row, ensure_ascii=False) + '\n')
        counts[kind] = {'columns': len(headers), 'window_rows': sum(by_move[kind].values())}

    gaps = Counter()
    gap_targets = {}
    applicable = Counter()
    for target, (observed, filled) in audit.items():
        applicable.update(observed)
        missing = sorted(observed - filled)
        gaps.update(missing)
        if missing:
            gap_targets[target] = missing
    result = {'capture_counts': counts, 'movement_status': by_move, 'applicable_targets': applicable,
              'missing_fields': gaps, 'missing_by_target': gap_targets}
    (output / 'field-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                            encoding='utf-8')
    print(json.dumps({'capture_counts': counts, 'movement_status': by_move, 'missing_fields': gaps},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    output = args.output_dir or args.folder
    output.mkdir(parents=True, exist_ok=True)
    main(args.folder, output)
