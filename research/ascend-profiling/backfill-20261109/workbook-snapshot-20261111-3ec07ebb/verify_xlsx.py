"""Check the exported workbook's tabs, row coverage, and Excel error cells."""

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def verify(path, capture_only=False):
    folder = path.parent
    counts = json.loads((folder / 'counts.json').read_text(encoding='utf-8'))
    scope = json.loads((folder / 'export-scope.json').read_text(encoding='utf-8'))
    seen = set()
    window_counts = Counter()
    with ZipFile(path) as workbook:
        info = ET.fromstring(workbook.read('xl/workbook.xml'))
        names = [x.attrib['name'] for x in info.find(NS + 'sheets')]
        assert names == [x['sheet'] for x in counts.values()], names
        if 'xl/sharedStrings.xml' in workbook.namelist():
            with workbook.open('xl/sharedStrings.xml') as data:
                strings = []
                for _, node in ET.iterparse(data, events=('end',)):
                    if node.tag == NS + 'si':
                        strings.append(''.join(x.text or '' for x in node.iter(NS + 't')))
                        node.clear()
        else:
            strings = []
        def cell_value(cell):
            value = cell.findtext(NS + 'v')
            kind = cell.attrib.get('t')
            if kind == 's':
                return strings[int(value)]
            if kind == 'inlineStr':
                return ''.join(t.text or '' for t in cell.iter(NS + 't'))
            return value

        for n, (kind, data) in enumerate(counts.items(), start=1):
            suffix = '-capture' if capture_only else ''
            with (folder / f'{kind}{suffix}.jsonl').open(encoding='utf-8') as source:
                headers = json.loads(next(source))
                expected_rows = list(map(json.loads, source)) if capture_only else []
            latest_windows = {}
            if scope.get('latest_only') and not capture_only:
                with (folder / f'{kind}-capture.jsonl').open(encoding='utf-8') as source:
                    compact_headers = json.loads(next(source))
                    window_col = compact_headers.index('窗口序号')
                    latest_windows = {r[0]: r[window_col] for r in map(json.loads, source)}
            roles = Counter()
            targets = set()
            with workbook.open(f'xl/worksheets/sheet{n}.xml') as sheet:
                for _, row in ET.iterparse(sheet, events=('end',)):
                    if row.tag != NS + 'row':
                        continue
                    index = int(row.attrib['r'])
                    if index <= 4:
                        if index == 4:
                            assert [cell_value(c) for c in row] == headers, data['sheet']
                        row.clear()
                        continue
                    values = {}
                    for cell in row:
                        addr = cell.attrib['r']
                        assert cell.attrib.get('t') != 'e', (data['sheet'], addr)
                        if capture_only:
                            prefix = addr.rstrip('0123456789')
                            col = 0
                            for letter in prefix:
                                col = col * 26 + ord(letter) - ord('A') + 1
                            values[col - 1] = cell_value(cell)
                            continue
                        if addr not in (f'A{index}', f'D{index}', f'E{index}'):
                            continue
                        values[addr[0]] = cell_value(cell)
                    if capture_only:
                        expected = expected_rows[index - 5]
                        for col, item in enumerate(expected):
                            actual = values.get(col)
                            if isinstance(item, (float, int)):
                                assert actual is not None and math.isclose(float(actual), item,
                                    rel_tol=1e-12, abs_tol=1e-15), (data['sheet'], index, col)
                            else:
                                assert actual == item or (actual is None and item == ''), (
                                    data['sheet'], index, col)
                        target, role = values[0], '采集'
                    else:
                        target, role = values.get('A'), values.get('D')
                        if latest_windows:
                            assert int(values['E']) == latest_windows[target], (
                                data['sheet'], target, values['E'])
                    assert target and role in ('采集', '逐核'), (data['sheet'], index)
                    roles[role] += 1
                    if role == '采集':
                        window_counts[target] += 1
                    targets.add(target)
                    row.clear()
            assert len(targets) == data['targets'], (data['sheet'], len(targets))
            assert roles['采集'] == data['window_rows'], roles
            assert roles['逐核'] == (0 if capture_only else data['core_rows']), roles
            assert not seen & targets
            seen.update(targets)
    assert window_counts == scope['targets'], 'Per-target capture count changed'
    assert seen == set(scope['targets']), 'Exported target IDs changed'
    print(f'PASS {len(seen)} targets across {len(names)} sheets. No Excel error cells.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=Path, nargs='?', default=HERE / '专家算子Profiling汇总.xlsx')
    parser.add_argument('--capture', action='store_true')
    args = parser.parse_args()
    verify(args.path, args.capture)
