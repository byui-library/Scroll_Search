import os,re,sys,glob,json
O,S=sys.argv[1],sys.argv[2]
pat=re.compile(r"\b(men'?s'?|mens|male|boys'?|gentlemen'?s)\s*(glee(\s*club)?|chorus|choir|quartet)|\bglee\s*club|\bmale\s*glee|\bgirls'?\s*glee|ladies'?\s*glee|\bglees\b",re.I)
files=sorted(glob.glob(O+'/ocr/t*.txt'))+sorted(glob.glob(O+'/pdftext/p*.txt'))+sorted(glob.glob(O+'/pdfocr/q*.txt'))
out=[]
for fp in files:
    raw=open(fp,encoding='utf-8',errors='replace').read()
    first,_,body=raw.partition('\n'); src=first.replace('SOURCE: ','').strip()
    t=re.sub(r'\s+',' ',body)
    ms=list(pat.finditer(t))
    if not ms: continue
    terms=sorted(set(re.sub(r'\s+',' ',m.group(0).lower()) for m in ms))
    snips=[]; last=-9999
    for m in ms:
        if m.start()-last<500: continue
        last=m.start(); snips.append(t[max(0,m.start()-300):m.end()+400])
    out.append({'source':src,'terms':terms,'n':len(ms),'snips':snips[:4]})
json.dump(out,open(S+'/glee_hits.json','w',encoding='utf-8'))
from collections import Counter
c=Counter(); [c.update(r['terms']) for r in out]
print(len(files),'pages',len(out),'with hits'); print(c.most_common(40))
