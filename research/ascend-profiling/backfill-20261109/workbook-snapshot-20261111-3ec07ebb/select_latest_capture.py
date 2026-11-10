"""Select the last verified capture of each target from the frozen workbook input."""

import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path


CAPTURE_STAMP = re.compile(r'OPPROF_(\d{14})_')


def select_core_rows(source, output, kind, selected, capture_headers):
    filename = f'{kind}.jsonl'
    counters = Counter()
    picked = set()
    with (source / filename).open(encoding='utf-8') as stream, (
        output / filename
    ).open('w', encoding='utf-8') as target_file:
        first = next(stream)
        target_file.write(first)
        headers = json.loads(first)
        idx = {k: headers.index(k) for k in ('采集来源', '窗口序号', '记录粒度', '核侧',
                                            'block_id', 'sub_block_id', '复算状态')}
        capture_source = capture_headers.index('采集来源')
        capture_window = capture_headers.index('窗口序号')
        cores = set()
        for line in stream:
            row = json.loads(line)
            target = row[0]
            reference = selected[target]
            if row[idx['窗口序号']] != reference[capture_window]:
                continue
            assert row[idx['采集来源']] == reference[capture_source], target
            if row[idx['记录粒度']] == '采集':
                assert target not in picked, target
                picked.add(target)
                if row[idx['复算状态']] == '四列已按同窗复算':
                    counters['windows_recomputed'] += 1
                cores.clear()
            else:
                assert row[idx['记录粒度']] == '逐核' and target in picked, target
                core = row[idx['block_id']], row[idx['sub_block_id']]
                assert core not in cores, (target, core)
                cores.add(core)
                side = row[idx['核侧']].lower()
                counters['core_rows'] += 1
                counters[f'core_role_{side}'] += 1
            target_file.write(line)
    assert picked == selected.keys()
    return counters


def main(source, output):
    output.mkdir(parents=True, exist_ok=True)
    counts = json.loads((source / 'counts.json').read_text(encoding='utf-8'))
    previous = json.loads((source / 'export-scope.json').read_text(encoding='utf-8'))
    targets = {}
    capture_counts = {}
    for kind, stats in counts.items():
        filename = f'{kind}-capture.jsonl'
        with (source / filename).open(encoding='utf-8') as stream:
            headers = json.loads(next(stream))
            source_column = headers.index('采集来源')
            window_column = headers.index('窗口序号')
            selected = {}
            previous_stamp = {}
            remote_seen = set()
            for row in map(json.loads, stream):
                target = row[0]
                window = row[window_column]
                if target in selected:
                    assert window > selected[target][window_column], target
                stamp = CAPTURE_STAMP.search(row[source_column])
                assert target not in remote_seen, target
                if stamp:
                    assert stamp[1] >= previous_stamp.get(target, ''), target
                    previous_stamp[target] = stamp[1]
                else:
                    # The audited HiDev recapture is appended after local source captures.
                    assert row[source_column].startswith('/workspace/'), row[source_column]
                    remote_seen.add(target)
                selected[target] = row
        assert len(selected) == stats['targets'], kind
        assert not targets.keys() & selected.keys(), kind
        with (output / filename).open('w', encoding='utf-8') as stream:
            stream.write(json.dumps(headers, ensure_ascii=False) + '\n')
            for row in selected.values():
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
        targets.update(dict.fromkeys(selected, 1))
        print(kind, stats['window_rows'], '→', len(selected))
        detail = select_core_rows(source, output, kind, selected, headers)
        for field in ('core_rows', 'core_role_aiv', 'core_role_aic', 'windows_recomputed'):
            if field in stats or field in detail:
                stats[field] = detail[field]
        stats['window_rows'] = len(selected)
        print(kind, detail['core_rows'], 'core rows')
        capture_counts[kind] = {'columns': len(headers), 'window_rows': len(selected)}
    assert targets.keys() == previous['targets'].keys()
    outputs = {'counts.json': counts, 'field-audit.json': {'capture_counts': capture_counts},
               'export-scope.json': {**previous, 'targets': targets, 'latest_only': True}}
    for name, contents in outputs.items():
        (output / name).write_text(json.dumps(contents, ensure_ascii=False, indent=2),
                                   encoding='utf-8')
    shutil.copyfile(source / 'as-of.txt', output / 'as-of.txt')


if __name__ == '__main__':
    main(*map(Path, sys.argv[1:]))
