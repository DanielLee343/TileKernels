"""Write the validated workbook input when the in-memory exporter cannot fit."""

import json
import sys
from pathlib import Path

import xlsxwriter


HERE = Path(__file__).resolve().parent
COLORS = {'vector': '#244B70', 'cube': '#356352', 'mix': '#634F76'}
WIDTHS = [75, 54, 49, 12, 12, 11, 12, 14, 35, 39, 24, 24, 28,
          19, 13, 15, 17, 17, 64, 28, 55, 41, 56, 50]


def main(folder, output_name):
    counts = json.loads((folder / 'counts.json').read_text(encoding='utf-8'))
    scope = json.loads((folder / 'export-scope.json').read_text(encoding='utf-8'))
    output = folder / output_name
    temporary = output.with_suffix('.partial.xlsx')
    stamp_path = folder / 'as-of.txt'
    as_of = stamp_path.read_text(encoding='utf-8').strip() if stamp_path.is_file() else ''
    with xlsxwriter.Workbook(temporary, {
        'constant_memory': True,
        'strings_to_formulas': False,
        'strings_to_urls': False,
        'tmpdir': str(folder),
    }) as workbook:
        title = workbook.add_format({'font_size': 15, 'bold': True, 'font_color': '#162B3D'})
        summary = workbook.add_format({'bold': True, 'font_color': '#253E55'})
        note = workbook.add_format({'italic': True, 'font_color': '#465666'})
        for kind, data in counts.items():
            sheet = workbook.add_worksheet(data['sheet'])
            sheet.hide_gridlines(2)
            sheet.freeze_panes(4, 0)
            sheet.set_tab_color(COLORS[kind])
            for column, width in enumerate(WIDTHS):
                sheet.set_column(column, column, width)
            sheet.set_column(len(WIDTHS), data['columns'] - 1, 24)
            sheet.set_row(0, 25)
            sheet.write_string(0, 0, data['sheet'] + ' 专家 profiling', title)
            sheet.write_row(1, 0, ['目标数', data['targets'], '采集记录', data['window_rows'],
                                   '逐核记录', data['core_rows']], summary)
            message = ('每个目标仅保留最新一份已验收采集。NA 为工具原始缺值，复算值单列。'
                       if scope.get('latest_only') else
                       '仅列已验收且有原始表的采集。NA 为工具原始缺值，复算值单列。')
            sheet.write_string(2, 0, (as_of + ' 快照。' if as_of else '') + message, note)
            sheet.set_row(3, 43)
            header_style = workbook.add_format({'bg_color': COLORS[kind], 'font_color': '#FFFFFF',
                                                'bold': True, 'text_wrap': True, 'valign': 'vcenter'})
            with (folder / f'{kind}.jsonl').open(encoding='utf-8') as stream:
                headers = json.loads(next(stream))
                assert len(headers) == data['columns']
                sheet.write_row(3, 0, headers, header_style)
                for row_index, line in enumerate(stream, start=4):
                    values = json.loads(line)
                    assert len(values) == data['columns']
                    assert sheet.write_row(row_index, 0, values) == 0
            assert row_index == 3 + data['window_rows'] + data['core_rows']
            sheet.autofilter(3, 0, row_index, data['columns'] - 1)
            print(f"{data['sheet']}: {data['window_rows']} windows, {data['core_rows']} core rows", flush=True)
    temporary.replace(output)


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE,
         sys.argv[2] if len(sys.argv) > 2 else '专家算子Profiling汇总.xlsx')
