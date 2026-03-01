#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except:
    AKSHARE_AVAILABLE = False

TOUZI_DIR = os.path.expanduser('~/Code/touzi')
REPORT_DIR = os.path.join(TOUZI_DIR, 'reports')

COMPANY_CODES = {
    '贵州茅台': '600519', '五粮液': '000858', '海康威视': '002415',
    '中国平安': '601318', '格力电器': '000651', '伊利股份': '600887',
    '上海机场': '600009', '洋河股份': '002304', '东阿阿胶': '000423',
    '东鹏饮料': '603959', '涪陵榨菜': '002507', '片仔癀': '600436', '天津达仁堂': '600329',
}
INDUSTRIES = {
    '贵州茅台': '白酒', '五粮液': '白酒', '海康威视': '安防', '中国平安': '保险',
    '格力电器': '家电', '伊利股份': '食品饮料', '上海机场': '交通运输', '洋河股份': '白酒',
    '东阿阿胶': '中药', '东鹏饮料': '食品饮料', '涪陵榨菜': '食品饮料',
    '片仔癀': '中药', '天津达仁堂': '中药',
}

def get_stock_price(code):
    if not AKSHARE_AVAILABLE: return None, None
    try:
        df = ak.stock_zh_a_spot_em()
        s = df[df['代码'] == code]
        return (s.iloc[0]['最新价'], s.iloc[0]['涨跌幅']) if not s.empty else (None, None)
    except: return None, None

def get_hist(code, d=5):
    if not AKSHARE_AVAILABLE: return None
    try:
        ed = datetime.now().strftime('%Y%m%d')
        sd = (datetime.now() - timedelta(days=d+10)).strftime('%Y%m%d')
        df = ak.stock_zh_a_hist(symbol=code, period='daily', start_date=sd, end_date=ed, adjust='qfq')
        return df.tail(d) if not df.empty else None
    except: return None

def analyze():
    rs = []
    for co, cd in COMPANY_CODES.items():
        p, c = get_stock_price(cd)
        h = get_hist(cd, 5)
        c5 = ((h.iloc[-1]['收盘'] - h.iloc[0]['收盘']) / h.iloc[0]['收盘'] * 100) if h is not None and len(h) >= 2 else None
        rs.append({'co': co, 'cd': cd, 'p': p, 'c': c, 'c5': c5, 'ind': INDUSTRIES.get(co, '其他')})
    return rs

def gen_report():
    os.makedirs(REPORT_DIR, exist_ok=True)
    rs = analyze()
    vp = [r for r in rs if r['p']]
    avgc = sum(r['c'] for r in vp) / len(vp) if vp else 0
    v5 = [r for r in rs if r['c5']]
    avg5 = sum(r['c5'] for r in v5) / len(v5) if v5 else 0
    tf = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rf = os.path.join(REPORT_DIR, f'report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md')
    inds = {}
    for r in rs:
        inds.setdefault(r['ind'], []).append(r['co'])
    with open(rf, 'w') as f:
        f.write(f'# 投资组合监控报告

**生成时间**: {tf}

')
        f.write(f'## 今日概况

|指标|数值|
|---|---|
|持仓数|{len(rs)}|
|今日平均|{avgc:+.2f}%|
|5日平均|{avg5:+.2f}%|

')
        f.write(f'## 行业分布

')
        for i, cos in inds.items(): f.write(f'- **{i}**: {chr(44).join(cos)}
')
        f.write(f'
## 个股

|公司|代码|现价|今日|5日|行业|
|---|---|---|---|---|---|
')
        for r in rs:
            ps = f"¥{r['p']:.2f}" if r['p'] else 'N/A'
            cs = f"{r['c']:+.2f}%" if r['c'] else 'N/A'
            c5s = f"{r['c5']:+.2f}%" if r['c5'] else 'N/A'
            f.write(f"|{r['co']}|{r['cd']}|{ps}|{cs}|{c5s}|{r['ind']}|
")
        f.write(f'
## 操作建议

')
        st = [r for r in rs if r['c'] and r['c'] > 3]
        wk = [r for r in rs if r['c'] and r['c'] < -3]
        if st: f.write('**强势**:
' + '
'.join(f'- {x["co"]}: +{x["c"]:.2f}%' for x in st) + '

')
        if wk: f.write('**下跌**:
' + '
'.join(f'- {x["co"]}: {x["c"]:.2f}%' for x in wk) + '

')
        f.write(f'**整体**: {"偏多" if avgc > 1 else "偏弱" if avgc < -1 else "震荡"}
')
    return rf, rs

if __name__ == '__main__':
    if not AKSHARE_AVAILABLE: exit(1)
    rf, rs = gen_report()
    print(f'OK: {rf}')
