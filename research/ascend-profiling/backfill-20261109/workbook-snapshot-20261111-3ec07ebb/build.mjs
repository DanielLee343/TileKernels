import fs from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline';
import { join, resolve } from 'node:path';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const captureIndex = process.argv.indexOf('--capture');
const captureOnly = captureIndex !== -1;
const folder = captureOnly ? resolve(process.argv[captureIndex + 1])
  : fileURLToPath(new URL('.', import.meta.url));
const workbook = Workbook.create();
const renderOnly = process.argv.includes('--render-only');
const counts = JSON.parse(await fs.readFile(join(folder, 'counts.json'), 'utf8'));
const scope = JSON.parse(await fs.readFile(join(folder, 'export-scope.json'), 'utf8'));
const captureCounts = captureOnly
  ? JSON.parse(await fs.readFile(join(folder, 'field-audit.json'), 'utf8')).capture_counts : {};
const asOf = captureOnly ? (await fs.readFile(join(folder, 'as-of.txt'), 'utf8')).trim() : '';
const rowStart = 4;
const chunkSize = 512;
const palette = { vector: '#244B70', cube: '#356352', mix: '#634F76' };

for (const [kind, data] of Object.entries(counts)) {
  const sheet = workbook.worksheets.add(data.sheet);
  const columns = captureOnly ? captureCounts[kind].columns : data.columns;
  sheet.showGridLines = false;
  sheet.tabColor = palette[kind];
  const title = scope.latest_only ? ' · 每个目标最新采集' : captureOnly ? ' · 采集汇总' : '';
  sheet.getRange('A1').values = [[`${data.sheet} 专家 profiling${title}`]];
  sheet.getRange('A1').format.font = { name: 'Arial', size: 15, bold: true, color: '#162B3D' };
  sheet.getRange('A2:F2').values = [captureOnly
    ? ['目标数', data.targets, '采集记录', data.window_rows, '台账快照', asOf]
    : ['目标数', data.targets, '采集记录', data.window_rows, '逐核记录', data.core_rows]];
  sheet.getRange('A3').values = [[
    scope.full_aggregation
      ? '每个目标一行。AIC 和 AIV 分开汇总。原分母指工具计算核带宽时采用的时间，纯核用核耗时，混合用任务耗时。缺值或分母为零时留空。'
      : scope.latest_only
      ? '每个目标只保留最新已验收的采集。缺值按原采集保留。周期加权比率为 0–1 小数。'
      : captureOnly
      ? '每次采集一行。AIV 与 AIC 分开汇总。周期加权比率为 0–1 小数。合计活动时间可超过任务耗时。'
      : scope.accepted_only
      ? '仅列已验收且有原始表的采集。NA 为工具原始缺值，复算值单列。'
      : '按采集窗口分别列出原始值及复算值。NA 为工具原始缺值，复算值单列。',
  ]];
  sheet.getRange('A2:F2').format.font = { name: 'Arial', size: 10, bold: true, color: '#253E55' };
  for (const key of ['B2', 'D2', 'F2']) sheet.getRange(key).format.horizontalAlignment = 'left';
  sheet.getRange('A3').format.font = { name: 'Arial', size: 10, italic: true, color: '#465666' };
  sheet.getRange('A1').format.rowHeight = 25;
  sheet.getRange('A3').format.rowHeight = 18;

  const stream = createInterface({
    input: createReadStream(join(folder, `${kind}${captureOnly ? '-capture' : ''}.jsonl`),
      { encoding: 'utf8' }), crlfDelay: Infinity,
  });
  let first = true;
  let offset = rowStart;
  let chunk = [];
  for await (const line of stream) {
    const row = JSON.parse(line);
    if (row.length !== columns) throw new Error(`${kind} column count changed`);
    if (first) {
      const header = sheet.getRangeByIndexes(rowStart - 1, 0, 1, columns);
      header.values = [row];
      header.format.fill = palette[kind];
      header.format.font = { name: 'Arial', size: 10, bold: true, color: '#FFFFFF' };
      header.format.rowHeight = scope.full_aggregation ? 65 : captureOnly ? 52 : 39;
      header.format.wrapText = true;
      header.format.verticalAlignment = 'center';
      first = false;
      continue;
    }
    chunk.push(row);
    if (chunk.length === chunkSize) {
      sheet.getRangeByIndexes(offset, 0, chunk.length, columns).values = chunk;
      offset += chunk.length;
      chunk = [];
    }
  }
  if (chunk.length > 0) {
    sheet.getRangeByIndexes(offset, 0, chunk.length, columns).values = chunk;
    offset += chunk.length;
  }
  if (offset - rowStart !== data.window_rows + (captureOnly ? 0 : data.core_rows)) {
    throw new Error(`${kind} row count changed`);
  }
  const widths = captureOnly ? [54, 45, 42, 13, 18, 26, 29, 39, 13, 16, 26, 37, 36, 40, 60, 56, 48]
    : [75, 54, 49, 11, 12, 10, 11, 13, 35, 39, 22, 24, 24,
    19, 13, 15, 17, 17, 64, 28, 55, 41, 56, 50];
  for (const [column, width] of widths.entries()) {
    sheet.getRangeByIndexes(rowStart - 1, column, 1, 1).format.columnWidth = width;
  }
  sheet.getRangeByIndexes(rowStart - 1, widths.length, 1, columns - widths.length)
    .format.columnWidth = scope.full_aggregation ? 35 : captureOnly ? 28 : 21;
  sheet.freezePanes.freezeRows(rowStart);
  console.log(`${data.sheet}: ${data.targets} targets, ${data.window_rows} windows, ${data.core_rows} cores`);
}

workbook.recalculate();
for (const [kind, data] of Object.entries(counts)) {
  const check = await workbook.inspect({
    kind: 'table', range: `${data.sheet}!A4:H8`, include: 'values', tableMaxRows: 5, tableMaxCols: 8,
  });
  console.log(check.ndjson);
  const blob = await workbook.render({ sheetName: data.sheet, range: 'A1:H9', scale: 1, format: 'png' });
  await fs.writeFile(join(folder, `preview-${captureOnly ? 'capture-' : ''}${data.sheet}.png`),
    new Uint8Array(await blob.arrayBuffer()));
  if (scope.full_aggregation) {
    const aggregateRange = kind === 'vector' ? 'BD4:BI8' : 'BK4:BQ8';
    const aggregatePreview = await workbook.render({
      sheetName: data.sheet, range: aggregateRange, scale: 1, format: 'png',
    });
    await fs.writeFile(join(folder, `preview-aggregate-${data.sheet}.png`),
      new Uint8Array(await aggregatePreview.arrayBuffer()));
  }
}
if (!renderOnly) {
  const output = await SpreadsheetFile.exportXlsx(workbook);
  const filename = scope.full_aggregation ? '专家算子Profiling-采集精简版-全局指标.xlsx'
    : scope.latest_only ? '专家算子Profiling-采集精简版-每目标最新.xlsx'
    : captureOnly ? '专家算子Profiling-采集精简版.xlsx' : '专家算子Profiling汇总.xlsx';
  await output.save(join(folder, filename));
}
