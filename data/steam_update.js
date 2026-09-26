// Steam のユーザーレビュー数を、台帳（titles.csv の steam_appid がある作品）のぶん取って milestones.csv の末尾に追記する。
// 使い方：node D:/tas9_labo/web/notes/data/steam_update.js   （同じ日に2回走らせても二重には足さない）
// 数字は Steam が公式に返す query_summary.total_reviews（全言語・全購入区分）。本数への換算は分析の時に行う（README 参照）。
const fs = require('fs'), path = require('path');
const D = __dirname;

function parse(t) {
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
  return { h, rows: rows.filter(r => r.some(x => x.trim() !== '')) };
}
function readFile(f) {
  let t = fs.readFileSync(path.join(D, f), 'utf8');
  const bom = t.charCodeAt(0) === 0xFEFF; if (bom) t = t.slice(1);
  const eol = (t.match(/\r\n/g) || []).length > (t.match(/\n/g) || []).length / 2 ? '\r\n' : '\n';
  return { f, t: t.replace(/\r\n/g, '\n'), bom, eol };
}
function cell(s) { return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }

(async () => {
  const T = readFile('titles.csv'), tp = parse(T.t), ti = Object.fromEntries(tp.h.map((k, i) => [k, i]));
  const M = readFile('milestones.csv'), mp = parse(M.t), mi = Object.fromEntries(mp.h.map((k, i) => [k, i]));
  if (ti.steam_appid === undefined) { console.log('NG titles.csv に steam_appid の列が無い'); process.exit(1); }
  const jst = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
  const have = new Set(mp.rows.map(r => [r[mi.id], r[mi.metric], r[mi.as_of]].join('|')));
  const out = []; let n = 0, ng = 0;
  for (const r of tp.rows) {
    const id = r[ti.id], app = (r[ti.steam_appid] || '').trim();
    if (!/^\d+$/.test(app)) continue;
    if (have.has([id, 'reviews', jst].join('|'))) { console.log('skip ' + id + '（今日の分は済み）'); continue; }
    const url = 'https://store.steampowered.com/appreviews/' + app + '?json=1&language=all&purchase_type=all&num_per_page=0&filter=all';
    let j = null;
    try { const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }); j = await res.json(); } catch (e) { console.log('NG ' + id + ' ' + String(e)); ng++; continue; }
    const q = j && j.query_summary;
    if (!q || typeof q.total_reviews !== 'number') { console.log('NG ' + id + ' 返事に数字が無い'); ng++; continue; }
    const note = '好評' + q.total_positive + '・不評' + q.total_negative + '。全言語・全購入区分。appid ' + app;
    out.push([id, 'reviews', String(q.total_reviews), '件', 'exact', 'world', 'steam', 'official', jst, 'Steam（ユーザーレビュー数）', url, note].map(cell).join(','));
    n++;
    await new Promise(res => setTimeout(res, 400));
  }
  if (out.length) {
    let t = M.t; if (!t.endsWith('\n')) t += '\n';
    t += out.join('\n') + '\n';
    fs.writeFileSync(path.join(D, M.f), (M.bom ? '\uFEFF' : '') + t.replace(/\n/g, M.eol));
  }
  console.log('ok steam reviews ' + n + '件 追記（' + jst + '）' + (ng ? '・取れなかった作品 ' + ng : ''));
  process.exit(ng ? 1 : 0);
})();
