// 節目台帳の形の確認。使い方：node D:/tas9_labo/web/notes/data/check.js
// 列の並び・日付・整数・選択肢・id の対応・重複を見る。NG なら 1 で終わる。
const fs = require('fs'), path = require('path');
const D = __dirname;

function readCsv(f) {
  let t = fs.readFileSync(path.join(D, f), 'utf8');
  if (t.charCodeAt(0) === 0xFEFF) t = t.slice(1);
  t = t.replace(/\r\n/g, '\n');
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (q) { if (c === '"') { if (t[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true;
    else if (c === ',') { row.push(cell); cell = ''; }
    else if (c === '\n') { row.push(cell); rows.push(row); row = []; cell = ''; }
    else cell += c;
  }
  if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
  const h = rows.shift().map(s => s.trim());
  const body = rows.filter(r => r.some(x => x.trim() !== ''));
  return { h, rows: body.map(r => Object.fromEntries(h.map((k, i) => [k, (r[i] || '').trim()]))) };
}

const T_H = ['id', 'title_ja', 'developer', 'publisher', 'origin_jp', 'release_date', 'platforms', 'team_size', 'team_size_source', 'size_class', 'note'];
const M_H = ['id', 'metric', 'value', 'unit', 'precision', 'scope', 'channel', 'basis', 'as_of', 'source_name', 'source_url', 'note'];
const EN = {
  metric: ['units_sold', 'units_shipped', 'units_shipped_dl', 'players', 'revenue'],
  unit: ['本', '人', '円'],
  precision: ['exact', 'at_least'],
  scope: ['world', 'japan'],
  channel: ['all', 'package', 'digital', 'steam'],
  basis: ['official', 'estimate', 'press'],
};
const E = [];
const err = m => E.push(m);
const isDate = s => /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(Date.parse(s));

const T = readCsv('titles.csv'), M = readCsv('milestones.csv');
if (T.h.join() !== T_H.join()) err('titles.csv の列が違う: ' + T.h.join(','));
if (M.h.join() !== M_H.join()) err('milestones.csv の列が違う: ' + M.h.join(','));

const ids = new Set(), rel = {};
T.rows.forEach((r, i) => {
  const n = 'titles.csv ' + (i + 2) + '行目 ' + r.id + ': ';
  if (!/^[a-z0-9-]+$/.test(r.id)) err(n + 'id は小文字英数字とハイフンだけ');
  if (ids.has(r.id)) err(n + 'id が重複');
  ids.add(r.id); rel[r.id] = r.release_date;
  if (!r.title_ja) err(n + 'title_ja が空');
  if (!['0', '1'].includes(r.origin_jp)) err(n + 'origin_jp は 0 か 1');
  if (!isDate(r.release_date)) err(n + 'release_date が日付でない');
  if (r.size_class && !['S', 'M', 'L'].includes(r.size_class)) err(n + 'size_class は S/M/L か空');
  if (r.team_size && !/^\d+(-\d+)?$/.test(r.team_size)) err(n + 'team_size は数字か範囲（3-40）');
  if ((r.team_size || r.size_class) && !r.team_size_source) err(n + '人数・規模を書くなら team_size_source が要る');
});

const seen = new Set();
M.rows.forEach((r, i) => {
  const n = 'milestones.csv ' + (i + 2) + '行目 ' + r.id + ': ';
  if (!ids.has(r.id)) err(n + 'titles.csv に無い id');
  for (const k in EN) if (!EN[k].includes(r[k])) err(n + k + ' は ' + EN[k].join('/') + ' のどれか（今: ' + r[k] + '）');
  if (!/^\d+$/.test(r.value)) err(n + 'value は整数・桁区切りなし');
  if (!isDate(r.as_of)) err(n + 'as_of が日付でない');
  if (rel[r.id] && isDate(r.as_of) && r.as_of < rel[r.id]) err(n + 'as_of が発売日より前');
  if (!/^https?:\/\//.test(r.source_url)) err(n + 'source_url が URL でない');
  if (!r.source_name) err(n + 'source_name が空');
  if (/^units/.test(r.metric) && r.unit !== '本') err(n + 'units_* の unit は 本');
  if (r.metric === 'players' && r.unit !== '人') err(n + 'players の unit は 人');
  if (r.metric === 'revenue' && r.unit !== '円') err(n + 'revenue の unit は 円');
  const key = [r.id, r.metric, r.scope, r.channel, r.as_of, r.source_url].join('|');
  if (seen.has(key)) err(n + '同じ作品・指標・時点・出典の重複');
  seen.add(key);
});

// ---- 指標台帳 ----
const DF_H = ['indicator_id', 'name_ja', 'unit', 'definition', 'default_source'];
const I_H = ['indicator_id', 'entity', 'period_end', 'value', 'unit', 'basis', 'source_name', 'source_url', 'note'];
const DF = readCsv('indicator_defs.csv'), I = readCsv('indicators.csv');
if (DF.h.join() !== DF_H.join()) err('indicator_defs.csv の列が違う: ' + DF.h.join(','));
if (I.h.join() !== I_H.join()) err('indicators.csv の列が違う: ' + I.h.join(','));
const defUnit = {};
DF.rows.forEach((r, i) => {
  const n = 'indicator_defs.csv ' + (i + 2) + '行目 ' + r.indicator_id + ': ';
  if (!/^[a-z0-9_]+$/.test(r.indicator_id)) err(n + 'indicator_id は小文字英数字とアンダースコア');
  if (defUnit[r.indicator_id]) err(n + 'indicator_id が重複');
  if (!r.unit) err(n + 'unit が空');
  defUnit[r.indicator_id] = r.unit;
});
const seenI = new Set();
I.rows.forEach((r, i) => {
  const n = 'indicators.csv ' + (i + 2) + '行目 ' + r.indicator_id + '/' + r.entity + ': ';
  if (!defUnit[r.indicator_id]) err(n + 'indicator_defs.csv に無い指標');
  else if (defUnit[r.indicator_id] !== r.unit) err(n + 'unit が定義と違う（定義: ' + defUnit[r.indicator_id] + '）');
  if (!/^[a-z0-9-]+$/.test(r.entity)) err(n + 'entity は小文字英数字とハイフン');
  if (!isDate(r.period_end)) err(n + 'period_end が日付でない');
  if (!/^-?\d+(\.\d+)?$/.test(r.value)) err(n + 'value は数字（桁区切りなし）');
  if (!EN.basis.includes(r.basis)) err(n + 'basis は ' + EN.basis.join('/'));
  if (!/^https?:\/\//.test(r.source_url)) err(n + 'source_url が URL でない');
  if (!r.source_name) err(n + 'source_name が空');
  const key = [r.indicator_id, r.entity, r.period_end, r.source_url].join('|');
  if (seenI.has(key)) err(n + '同じ指標・主体・時点・出典の重複');
  seenI.add(key);
});

if (E.length) { console.log('NG ' + E.length + '件'); E.forEach(e => console.log(' - ' + e)); process.exit(1); }
console.log('ok titles ' + T.rows.length + ' / milestones ' + M.rows.length + ' / indicators ' + I.rows.length + '（定義 ' + DF.rows.length + '）');
