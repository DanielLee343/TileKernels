"""Read-only extraction of one msOpProf capture and its audited outbound data."""

import csv
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


TABLES = ('OpBasicInfo', 'ArithmeticUtilization', 'L2Cache', 'Memory',
          'MemoryL0', 'MemoryUB', 'PipeUtilization', 'ResourceConflictRatio')
MOVE = re.compile(
    r'DBI record core:(\d+);pc:0x([0-9a-f]+);dst:\(type:GM;addr:0x([0-9a-f]+);'
    r'stride:(\d+);loop1Stride:(\d+);loop2Stride:(\d+)\);src:\(type:UB;[^)]*\);'
    r'nBurst:(\d+);lenBurst:(\d+);dataType:[^;]+;loop1Size:(\d+);loop2Size:(\d+);'
    r'leftPaddingNum:\d+;rightPaddingNum:\d+', re.IGNORECASE)
NORMAL = re.compile(
    r'DBI record MemRecord serialNo:\d+;pc:0x([0-9a-f]+);'
    r'dst:\(type:GM;addr:0x([0-9a-f]+);memSize:(\d+)\);'
    r'src:\(type:UB;addr:0x[0-9a-f]+;memSize:(\d+)\);', re.IGNORECASE)
DERIVED = ('向量核搬出请求字节 (B)', '工具计入 UB 侧字节 (B)',
           '复算 aiv_ub_to_gm_bw (GB/s)', '复算 aiv_ub_read_bw_gm (GB/s)',
           '复算 aiv_mte3_active_bw (GB/s)', '复算 UB_to_GM_bw_usage_rate (%)')


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def load_window(folder, basic_path=None):
    folder = Path(folder)
    basic_path = Path(basic_path) if basic_path else folder / 'OpBasicInfo.csv'
    suffix = basic_path.stem.removeprefix('OpBasicInfo')
    basic, = read_csv(basic_path)
    values = defaultdict(dict)
    expected_keys = None
    for table in TABLES[1:]:
        rows = read_csv(folder / (table + suffix + '.csv'))
        keys = set()
        for row in rows:
            key = (int(row['block_id']), row['sub_block_id'])
            if key in keys:
                raise ValueError(f'duplicate {table} row {key}')
            keys.add(key)
            for field, value in row.items():
                if not field or field in ('block_id', 'sub_block_id'):
                    continue
                if field in values[key] and values[key][field] != value:
                    raise ValueError(f'inconsistent {field} in {table} row {key}')
                values[key][field] = value
        if expected_keys is None:
            expected_keys = keys
        elif keys != expected_keys:
            raise ValueError(f'inconsistent row keys in {table}')
    return basic, values


def audit_requested(audit):
    if 'per_vector_block_requested_bytes' in audit:
        return {int(k): int(v) for k, v in audit['per_vector_block_requested_bytes'].items()}
    if 'per_vector_block_bytes_from_addresses' in audit:
        return {int(k): int(v) for k, v in audit['per_vector_block_bytes_from_addresses'].items()}
    if 'per_core' in audit:
        return {int(row['block']): int(row['dbi_bytes']) for row in audit['per_core']}
    return {}


def ub_side_bytes(log, expected):
    """Use parsed MemRecord sizes and bind them to blocks using raw event addresses."""
    owners = defaultdict(set)
    requested = Counter()
    parsed = []
    with Path(log).open(encoding='utf-8', errors='replace') as file:
        for line in file:
            if 'dst:(type:GM;' not in line or 'src:(type:UB;' not in line:
                continue
            if 'DBI record core:' in line:
                match = MOVE.search(line)
                if not match:
                    raise ValueError('unhandled raw UB→GM record format')
                core, pc, base, stride, step1, step2, count, width, loop1, loop2 = match.groups()
                core, base = int(core), int(base, 16)
                stride, step1, step2, count, width, loop1, loop2 = map(
                    int, (stride, step1, step2, count, width, loop1, loop2))
                tile, vector = divmod(core, 3)
                if vector not in (0, 1):
                    raise ValueError('raw UB→GM record has unverified vector role')
                flat = tile * 2 + vector
                loop1, loop2 = (loop1, loop2) if loop1 and loop2 else (1, 1)
                requested[flat] += count * width * loop1 * loop2
                for k in range(loop2):
                    for j in range(loop1):
                        for i in range(count):
                            owners[int(pc, 16), base + k * step2 + j * step1 + i * stride].add(flat)
            elif 'DBI record MemRecord ' in line:
                match = NORMAL.search(line)
                if not match:
                    raise ValueError('unhandled parsed UB→GM record format')
                pc, addr, destination, source = match.groups()
                parsed.append((int(pc, 16), int(addr, 16), int(destination), int(source)))
    if not parsed or +Counter(expected) != +requested:
        raise ValueError('raw requests disagree with the audited per-core bytes')
    source_bytes = Counter()
    destination_bytes = Counter()
    for pc, addr, destination, source in parsed:
        options = owners.get((pc, addr), ())
        if len(options) != 1:
            raise ValueError('parsed address cannot be tied to exactly one audited block')
        flat, = options
        source_bytes[flat] += source
        destination_bytes[flat] += destination
    if +destination_bytes != +requested:
        raise ValueError('parsed destination bytes disagree with the audited bytes')
    return source_bytes


def numeric(value):
    if value in ('', 'NA', None):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def derive(basic, rows, log, audit, maximum=131.76):
    expected = audit_requested(audit)
    if not expected:
        raise ValueError('no independently audited per-core request bytes')
    mixed = basic['Op Type'] == 'mix'
    vector = {}
    for (block, subblock), row in rows.items():
        if subblock.startswith('vector'):
            flat = 2 * block + int(subblock.removeprefix('vector')) if mixed else block
            if flat in vector:
                raise ValueError('duplicate vector block identity')
            vector[flat] = row
    if set(expected) != set(vector):
        raise ValueError('audit blocks differ from the capture rows')
    source = ub_side_bytes(log, expected)
    observed = {i: numeric(row.get('UB_to_GM_datas(KB)')) for i, row in vector.items()}
    direct = {i: source[i] for i in vector}
    paired = {i: (source[2 * i] + source[2 * i + 1] if not mixed else
                  source[i] + source[i + 1] if i % 2 == 0 else 0) for i in vector}
    if not any(value is not None for value in observed.values()) or not any(
            all(value is None or abs(value * 1024 - candidate[i]) <= 0.00052
                for i, value in observed.items()) for candidate in (direct, paired)):
        raise ValueError('decoded UB-side bytes do not reconcile with Memory.csv')
    frequency = numeric(basic['Current Freq']) or numeric(basic['Rated Freq'])
    wall = numeric(basic['Task Duration(us)'])
    result = {}
    for flat, row in vector.items():
        time = wall if mixed else float(row['aiv_total_cycles']) / frequency
        active = numeric(row.get('aiv_mte3_time(us)'))
        scale = source[flat] * 10**6 / 2**30
        whole = scale / time if time and time > 0 else None
        key = (flat // 2, f'vector{flat % 2}') if mixed else (flat, 'vector0')
        result[key] = [expected[flat], source[flat], whole, whole,
                       scale / active if active and active > 0 else None,
                       min(100, 100 * whole / maximum) if whole is not None else None]
    return result
