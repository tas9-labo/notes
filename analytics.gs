/* notes.tas9.net のアクセス記録（自前）。Google Apps Script に貼って「ウェブアプリ」として公開する。
   受け口：ページからの送信（doPost）を、このスクリプトが紐づくスプレッドシートの「log」に1行ずつ書く。
   見る側：スプレッドシート自体（自分の Google アカウントだけが開ける）。summarize() が「集計」シートを作り直す。
   記録するもの：時刻・ページ・参照元・訪問者の印（ブラウザ内の乱数）・タイムゾーン・言語・画面幅・端末の種類。
   記録しないもの：IP・氏名・メール・cookie。年齢や性別は取れない。                                        */

var LOG = 'log', SUM = '集計';

function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var ss = SpreadsheetApp.getActive();
    var sh = ss.getSheetByName(LOG) || ss.insertSheet(LOG);
    if (sh.getLastRow() === 0) {
      sh.appendRow(['時刻', 'ページ', '参照元', '訪問者', 'タイムゾーン', '言語', '画面幅', '端末', 'UA']);
    }
    var ua = String(d.ua || '').slice(0, 200);
    sh.appendRow([new Date(), String(d.p || '').slice(0, 80), String(d.r || '').slice(0, 200),
                  String(d.v || '').slice(0, 40), String(d.tz || '').slice(0, 40), String(d.l || '').slice(0, 20),
                  Number(d.w) || '', deviceOf(ua, Number(d.w) || 0), ua]);
  } catch (err) {}
  return ContentService.createTextOutput('ok');
}

// 動作確認用（ブラウザで URL を開くと ok と出る）
function doGet() { return ContentService.createTextOutput('ok'); }

function deviceOf(ua, w) {
  if (/iPhone|Android.*Mobile/i.test(ua)) return 'スマホ';
  if (/iPad|Android/i.test(ua)) return 'タブレット';
  if (w && w < 700) return 'スマホ';
  return 'PC';
}

// 「集計」シートを作り直す（手動で実行するか、毎日のトリガーに登録）
function summarize() {
  var ss = SpreadsheetApp.getActive();
  var log = ss.getSheetByName(LOG);
  if (!log || log.getLastRow() < 2) return;
  var rows = log.getRange(2, 1, log.getLastRow() - 1, 8).getValues();
  var byDay = {}, byPage = {}, byDev = {}, byHour = {}, byRef = {}, byTz = {}, vis = {};
  rows.forEach(function (r) {
    var t = r[0] instanceof Date ? r[0] : new Date(r[0]);
    var day = Utilities.formatDate(t, 'Asia/Tokyo', 'yyyy-MM-dd');
    var hour = Utilities.formatDate(t, 'Asia/Tokyo', 'HH') + '時';
    var page = r[1] || '/', ref = refOf(r[2]), v = r[3] || '', dev = r[7] || '', tz = r[4] || '不明';
    inc(byDay, day); inc(byPage, page); inc(byDev, dev); inc(byHour, hour); inc(byRef, ref); inc(byTz, tz);
    if (!vis[day]) vis[day] = {}; vis[day][v] = 1;
  });
  var sh = ss.getSheetByName(SUM) || ss.insertSheet(SUM);
  sh.clear();
  var out = [['日付', '閲覧数', '訪問者数']];
  Object.keys(byDay).sort().reverse().forEach(function (d) { out.push([d, byDay[d], Object.keys(vis[d]).length]); });
  out.push([]);
  out = out.concat(table('ページ', byPage), [[]], table('参照元', byRef), [[]], table('端末', byDev), [[]],
                   table('時間帯', byHour, true), [[]], table('タイムゾーン（国の目安）', byTz));
  var width = 3;
  sh.getRange(1, 1, out.length, width).setValues(out.map(function (r) { while (r.length < width) r.push(''); return r; }));
  sh.getRange(1, 1, 1, width).setFontWeight('bold');
}

function table(title, obj, keepOrder) {
  var keys = Object.keys(obj);
  keys.sort(keepOrder ? undefined : function (a, b) { return obj[b] - obj[a]; });
  var rows = [[title, '閲覧数', '']];
  keys.forEach(function (k) { rows.push([k, obj[k], '']); });
  return rows;
}
function inc(o, k) { o[k] = (o[k] || 0) + 1; }
function refOf(r) {
  if (!r) return '直接（リンクなし）';
  var m = String(r).match(/^https?:\/\/([^\/]+)/);
  var h = m ? m[1] : String(r);
  if (/google\./.test(h)) return '検索（Google）';
  if (/bing\.com|yahoo\./.test(h)) return '検索（Bing/Yahoo）';
  if (/notes\.tas9\.net/.test(h)) return 'サイト内';
  return h;
}
