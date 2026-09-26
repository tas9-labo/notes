# -*- coding: utf-8 -*-
"""EDINET の API から有価証券報告書（XBRL の CSV）を取り、indicators.csv に数字を追記する。

使い方（どこから呼んでもよい）：
  py D:/tas9_labo/web/notes/data/edinet_fetch.py --auto [--days 45]   直近の提出分を探し、未記録なら追記（ルーティン用）
  py D:/tas9_labo/web/notes/data/edinet_fetch.py --doc S100YCGO        書類番号を指定して追記
  py D:/tas9_labo/web/notes/data/edinet_fetch.py --find [--days 45]    探すだけ（書かない）
  py D:/tas9_labo/web/notes/data/edinet_fetch.py --list-wip S100YCGO   仕掛品まわりの要素を一覧（entities.csv の wip_element を決める時に）

鍵：ユーザー環境変数 EDINET_API_KEY（README の手順で保存）。鍵は表示しない。
対象：entities.csv にある会社の「有価証券報告書」（docTypeCode 120）だけ。数字は XBRL の値をそのまま転記する。
追記の約束：同じ指標・主体・時点で同じ値が既にあれば足さない。値が違えば note に「別の出典と食い違い」と書いて足す（上書きしない）。
"""
import os, sys, io, csv, json, zipfile, re, datetime as dt, urllib.request, urllib.parse, time
sys.stdout.reconfigure(encoding='utf-8')
D = os.path.dirname(os.path.abspath(__file__))
API = 'https://api.edinet-fsa.go.jp/api/v2/'
VIEW = 'https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/{}.pdf'

def api_key():
    k = os.environ.get('EDINET_API_KEY')
    if not k and os.name == 'nt':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as h:
                k = winreg.QueryValueEx(h, 'EDINET_API_KEY')[0]
        except OSError:
            k = None
    if not k:
        sys.exit('NG EDINET_API_KEY が無い（data/README.md の手順で保存する）')
    return k.strip()

def get(url, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': 'notes-ledger/1.0'})
    with urllib.request.urlopen(req, timeout=180) as r:
        b = r.read()
    return b if binary else json.loads(b.decode('utf-8'))

def read_csv(path):
    raw = io.open(path, encoding='utf-8', newline='').read()
    bom = raw.startswith('\ufeff')
    if bom: raw = raw[1:]
    eol = '\r\n' if raw.count('\r\n') > raw.count('\n') / 2 else '\n'
    rows = list(csv.reader(io.StringIO(raw.replace('\r\n', '\n'))))
    return rows, bom, eol

def append_rows(path, new_rows):
    if not new_rows: return
    _, _, eol = read_csv(path)
    raw = io.open(path, encoding='utf-8', newline='').read()
    if not raw.endswith('\n'): raw += eol
    buf = io.StringIO(); csv.writer(buf, lineterminator='\n').writerows(new_rows)
    io.open(path, 'w', encoding='utf-8', newline='').write(raw + buf.getvalue().replace('\n', eol))

def entities():
    rows, _, _ = read_csv(os.path.join(D, 'entities.csv'))
    h = rows[0]
    out = {}
    for r in rows[1:]:
        if not any(x.strip() for x in r): continue
        d = dict(zip(h, r)); out[d['edinet_code']] = d
    return out

# ---- 探す ----
def find_docs(k, days, date_from=None, date_to=None):
    ents = entities(); codes = set(ents)
    today = dt.date.today(); found = []
    if date_from and date_to:
        span = [date_from + dt.timedelta(days=i) for i in range((date_to - date_from).days + 1)]
    else:
        span = [today - dt.timedelta(days=i) for i in range(days, -1, -1)]
    for d in span:
        if d.weekday() >= 5: continue
        try:
            j = get(API + 'documents.json?date=' + d.isoformat() + '&type=2&Subscription-Key=' + k)
        except Exception as e:
            print('NG 一覧', d, e); continue
        for r in j.get('results') or []:
            if r.get('docTypeCode') == '120' and r.get('edinetCode') in codes and r.get('csvFlag') == '1':
                found.append({'docID': r['docID'], 'edinetCode': r['edinetCode'], 'entity': ents[r['edinetCode']]['entity'],
                              'desc': r.get('docDescription') or '', 'submit': r.get('submitDateTime') or '', 'periodEnd': r.get('periodEnd') or ''})
        time.sleep(0.2)
    return found

# ---- 読む ----
def load_facts(k, doc_id):
    z = get(API + 'documents/' + doc_id + '?type=5&Subscription-Key=' + k, binary=True)
    zf = zipfile.ZipFile(io.BytesIO(z))
    name = [n for n in zf.namelist() if n.lower().endswith('.csv') and '/jpcrp' in n.lower()]
    if not name: sys.exit('NG ' + doc_id + ' に jpcrp の CSV が無い')
    name = name[0]
    m = re.search(r'_(\d{4}-\d{2}-\d{2})_', name)
    period_end = dt.date.fromisoformat(m.group(1))
    raw = zf.read(name)
    try: t = raw.decode('utf-16')
    except UnicodeDecodeError: t = raw.decode('utf-8-sig', errors='replace')
    rows = list(csv.reader(io.StringIO(t), delimiter='\t'))
    h = rows[0]; idx = {c: i for i, c in enumerate(h)}
    facts = []
    for r in rows[1:]:
        if len(r) < len(h): continue
        facts.append({'el': r[idx['要素ID']], 'name': r[idx['項目名']], 'ctx': r[idx['コンテキストID']], 'cons': r[idx['連結・個別']],
                      'per': r[idx['期間・時点']], 'unit': r[idx['単位']], 'val': r[idx['値']].strip()})
    return facts, period_end

REL = [('Prior4Year', 4), ('Prior3Year', 3), ('Prior2Year', 2), ('Prior1Year', 1), ('CurrentYear', 0)]
def years_back(ctx):
    for key, n in REL:
        if ctx.startswith(key): return n
    return None

def minus_years(d, n):
    try: return d.replace(year=d.year - n)
    except ValueError: return d.replace(year=d.year - n, day=28)

def num(v):
    v = v.replace(',', '').replace('△', '-').replace('－', '')
    if v in ('', '-'): return None
    try: return float(v)
    except ValueError: return None

def fmt(x, pct=False):
    if pct: return ('%.2f' % x).rstrip('0').rstrip('.') if '.' in ('%.2f' % x) else ('%.2f' % x)
    return str(int(round(x)))

def pick(facts, els=None, names=None, cons=None, ctx_ok=None):
    out = []
    for f in facts:
        if els and f['el'] not in els: continue
        if names and f['name'] not in names: continue
        if cons and f['cons'] not in cons: continue
        if ctx_ok and not ctx_ok(f['ctx']): continue
        if num(f['val']) is None: continue
        out.append(f)
    return out

def plain(ctx):  # メンバーなしのコンテキスト（連結・全社）
    return '_' not in ctx
def nonconsol(ctx):
    return ctx.endswith('_NonConsolidatedMember')

def extract(facts, period_end, ent, doc_id, desc):
    src_name = 'EDINET 有価証券報告書（' + (desc or doc_id) + '・書類番号 ' + doc_id + '）'
    src_url = VIEW.format(doc_id)
    rows = []
    def add(ind, yb, val, unit, note):
        pe = minus_years(period_end, yb).isoformat()
        rows.append([ind, ent['entity'], pe, val, unit, 'official', src_name, src_url, note])
    # 従業員数（連結・提出会社）5年
    for f in pick(facts, els=['jpcrp_cor:NumberOfEmployees'], ctx_ok=plain):
        yb = years_back(f['ctx'])
        if yb is not None: add('employees_consolidated', yb, fmt(num(f['val'])), '人', 'XBRL から機械で転記（jpcrp_cor:NumberOfEmployees・連結）')
    for f in pick(facts, els=['jpcrp_cor:NumberOfEmployees'], ctx_ok=nonconsol):
        yb = years_back(f['ctx'])
        if yb is not None: add('employees_parent', yb, fmt(num(f['val'])), '人', 'XBRL から機械で転記（提出会社）')
    # 平均年間給与（提出会社）
    for f in pick(facts, els=['jpcrp_cor:AverageAnnualSalaryInformationAboutReportingCompanyInformationAboutEmployees'], ctx_ok=nonconsol):
        yb = years_back(f['ctx'])
        if yb is not None: add('avg_salary_parent', yb, fmt(num(f['val'])), '円', 'XBRL から機械で転記（提出会社）。持株会社なら本社だけの値')
    # 研究開発費（連結・年額）
    rd = pick(facts, els=['jpcrp_cor:ResearchAndDevelopmentExpensesIncludedInGeneralAndAdministrativeExpensesAndManufacturingCostForCurrentPeriod'], ctx_ok=plain)
    tag = '一般管理費及び当期製造費用に含まれる研究開発費'
    if not rd:
        rd = pick(facts, els=['jpcrp_cor:ResearchAndDevelopmentExpensesResearchAndDevelopmentActivities'], ctx_ok=plain); tag = '研究開発費、研究開発活動'
    for f in rd:
        yb = years_back(f['ctx'])
        if yb is not None: add('rd_expense', yb, fmt(num(f['val'])), '円', 'XBRL から機械で転記（' + tag + '）')
    # 外国法人等の持株比率
    a = pick(facts, els=['jpcrp_cor:PercentageOfShareholdingsForeignersOtherThanIndividuals'], ctx_ok=lambda c: c.startswith('CurrentYearInstant'))
    b = pick(facts, els=['jpcrp_cor:PercentageOfShareholdingsForeignIndividuals'], ctx_ok=lambda c: c.startswith('CurrentYearInstant'))
    if a:
        x = num(a[0]['val']) * 100 + (num(b[0]['val']) * 100 if b else 0)
        add('foreign_ownership_pct', 0, '%.2f' % x, '%', 'XBRL から機械で転記（所有者別状況：外国法人等の個人以外＋個人）')
    # 売上高（連結）5年：日本基準は売上高、IFRS は売上収益
    sales = [f for f in pick(facts, ctx_ok=plain)
             if f['name'] in ('売上高、経営指標等', '売上収益、経営指標等', '営業収益、経営指標等') or f['name'].startswith('売上収益（IFRS）、経営指標等')]
    for f in sales:
        yb = years_back(f['ctx'])
        if yb is not None: add('net_sales_consolidated', yb, fmt(num(f['val'])), '円', 'XBRL から機械で転記（' + f['name'] + '）')
    # 営業利益（連結）：日本基準 jppfs、IFRS jpigp
    op = pick(facts, els=['jppfs_cor:OperatingIncome'], cons=['連結'], ctx_ok=plain)
    if not op: op = pick(facts, els=['jpigp_cor:OperatingProfitLossIFRS'], ctx_ok=plain)
    if not op: op = [f for f in pick(facts, cons=['連結'], ctx_ok=plain) if f['name'].startswith('営業利益')]
    for f in op:
        yb = years_back(f['ctx'])
        if yb is not None: add('operating_income_consolidated', yb, fmt(num(f['val'])), '円', 'XBRL から機械で転記（' + f['name'] + '）')
    # 仕掛品（連結・全社）と、会社ごとのゲーム仕掛品
    wip = pick(facts, els=['jppfs_cor:WorkInProcess'], cons=['連結'], ctx_ok=plain)
    if not wip: wip = pick(facts, els=['jpigp_cor:WorkInProcessCAIFRS'], ctx_ok=plain)
    for f in wip:
        yb = years_back(f['ctx'])
        if yb is not None: add('work_in_process_consolidated', yb, fmt(num(f['val'])), '円', 'XBRL から機械で転記（連結貸借対照表の仕掛品・全社' + ('・IFRS' if 'IFRS' in f['el'] else '') + '）')
    w = ent.get('wip_element', '').strip()
    if w:
        for f in pick(facts, els=[w], ctx_ok=plain):
            if f['cons'] == '個別': continue
            yb = years_back(f['ctx'])
            if yb is not None: add('game_wip', yb, fmt(num(f['val'])), '円', 'XBRL から機械で転記（会社固有の要素 ' + w.split(':')[-1] + '）')
    return rows

def existing_index(path):
    rows, _, _ = read_csv(path)
    h = rows[0]; i = {c: n for n, c in enumerate(h)}
    seen = {}
    for r in rows[1:]:
        if len(r) < len(h): continue
        seen.setdefault((r[i['indicator_id']], r[i['entity']], r[i['period_end']]), set()).add(r[i['value']])
    return seen

def same_number(a, b):
    try: return abs(float(a) - float(b)) < 0.005
    except ValueError: return a == b

def process(k, doc, dry=False):
    ents = entities()
    ent = ents.get(doc['edinetCode'])
    if not ent: print('skip', doc['docID'], '対象外'); return 0
    facts, period_end = load_facts(k, doc['docID'])
    rows = extract(facts, period_end, ent, doc['docID'], doc.get('desc', ''))
    path = os.path.join(D, 'indicators.csv')
    seen = existing_index(path)
    out = []
    for r in rows:
        key = (r[0], r[1], r[2]); vals = seen.get(key)
        if vals and any(same_number(v, r[3]) for v in vals): continue
        if vals: r[8] += '。別の出典と食い違い（既存: ' + '/'.join(sorted(vals)) + '）'
        out.append(r); seen.setdefault(key, set()).add(r[3])
    if dry:
        for r in out: print('  ', ' | '.join(r[:5]))
    else:
        append_rows(path, out)
    print('ok', doc['docID'], ent['entity'], '追記', len(out), '行（抽出', len(rows), '行・重複は除外）')
    return len(out)

def main():
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); return
    k = api_key()
    days = int(a[a.index('--days') + 1]) if '--days' in a else 45
    if a[0] == '--find':
        for d in find_docs(k, days): print(d['submit'][:10], d['docID'], d['entity'], d['desc'])
    elif a[0] == '--auto':
        docs = find_docs(k, days); n = 0
        if not docs: print('ok 新しい有報なし（過去', days, '日）'); return
        for d in docs: n += process(k, d)
        print('ok 合計', n, '行追記')
    elif a[0] == '--range':
        f, t = dt.date.fromisoformat(a[1]), dt.date.fromisoformat(a[2]); n = 0
        docs = find_docs(k, 0, f, t)
        if not docs: print('ok 対象の有報なし', f, '〜', t); return
        for d in docs: n += process(k, d, dry='--dry' in a)
        print('ok 合計', n, '行追記')
    elif a[0] == '--doc':
        doc_id = a[1]
        code = a[a.index('--code') + 1] if '--code' in a else None
        if not code:
            facts, _ = load_facts(k, doc_id)
            m = re.search(r'(E\d{5})', ' '.join(f['ctx'] for f in facts[:2000]))
            code = m.group(1) if m else None
        if not code: sys.exit('NG --code E0xxxx を付けて')
        process(k, {'docID': doc_id, 'edinetCode': code, 'desc': a[a.index('--desc') + 1] if '--desc' in a else ''}, dry='--dry' in a)
    elif a[0] == '--list-wip':
        facts, pe = load_facts(k, a[1])
        print('当期末', pe)
        for f in facts:
            if re.search('仕掛品|コンテンツ制作勘定|ソフトウエア仮勘定|ソフトウェア仮勘定|制作費', f['name']) and num(f['val']) is not None and '_' not in f['ctx'].replace('_NonConsolidatedMember', ''):
                print(' | '.join([f['el'], f['name'][:40], f['ctx'], f['cons'], f['val']]))
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
