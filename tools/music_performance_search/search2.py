"""Second-pass search: college ensemble mention + performance language nearby."""
import os, re, sys, json, glob

S = sys.argv[1]
ENS = r"(bands?|orchestras?|symphon(?:y|ic)|choirs?|chorus|choruses|chorale|glee clubs?|ensembles?|madrigal(?:s| singers)?|singers|a ?cappella|jazz (?:band|ensemble|combo)|stage band|pep band|marching band|concert band|wind ensemble|opera workshop|operetta|male quartet|ladies'? quartet|trio|octet|sextet|quartet)"
COL = r"(ricks|college|academy|r\.? ?c\.?|student|students'|viking|school|vikings|our|institution|music department|department)"
NAMED = r"(vikaliers?|collegians|a ?cappella choir|concert chorale|lyric choir|women'?s chorus|men'?s chorus|men'?s glee|ladies'? glee|girls'? glee|boys'? glee|college glee|glee club|college orchestra|college band|college choir|ricks choir|symphonic band|concert band|jazz band|stage band|chamber singers|madrigal singers|oratorio society|messiah|hiawatha|cantata|operetta|opera)"
PERF = r"(concerts?|recitals?|perform(?:ed|s|ing|ance|ances)?|present(?:ed|s|ing)?|sang|sing(?:s|ing)?|sung|play(?:ed|s|ing)|tour(?:ed|s|ing)?|festival|rendition|rendered|selections|numbers|conduct(?:ed|or|ing)|under the direction|directed by|director|program|audience|encore|appear(?:ed|ance)?|featur(?:ed|ing))"

pair = re.compile(COL + r"\W+(?:\w+\W+){0,3}?" + ENS, re.I)
named = re.compile(NAMED, re.I)
perf = re.compile(PERF, re.I)

files = sorted(glob.glob(os.path.join(S, 'ocr', 't*.txt'))) + sorted(glob.glob(os.path.join(S, 'pdftext', 'p*.txt'))) + sorted(glob.glob(os.path.join(S, 'pdfocr', '*.txt')))
out = []
for fp in files:
    raw = open(fp, encoding='utf-8', errors='replace').read()
    first, _, body = raw.partition('\n')
    src = first.replace('SOURCE: ', '')
    text = re.sub(r'\s+', ' ', body)
    cands = []
    for m in list(pair.finditer(text)) + list(named.finditer(text)):
        a, b = max(0, m.start() - 350), m.end() + 350
        w = text[a:b]
        pv = set(x.group(0).lower() for x in perf.finditer(w))
        strong = len(pv & {'concert', 'concerts', 'recital', 'recitals', 'performed', 'performance', 'sang', 'presented', 'rendition', 'tour', 'toured', 'conducted', 'under the direction', 'directed by', 'audience', 'selections', 'numbers'})
        if len(pv) >= 2 and strong >= 1:
            cands.append((len(pv) + 2 * strong, m.start(), m.group(0)))
    if cands:
        cands.sort(reverse=True)
        sc, pos, term = cands[0]
        terms = sorted(set(c[2].lower() for c in cands))[:8]
        out.append({'file': fp, 'source': src, 'score': sc, 'pos': pos, 'terms': terms, 'snippet': text[max(0, pos - 250):pos + 300], 'n': len(cands)})
json.dump(out, open(os.path.join(S, 'hits2.json'), 'w', encoding='utf-8'))
print(len(files), 'pages;', len(out), 'hits')
