"""Parallel worker for remaining failed PDFs: extract text; render low-text pages for OCR.
Usage: pdfx3.py S START K N   (handles failed PDF indices >= START where index % N == K)"""
import sys, os, json, time
import pymupdf

S, START, K, N = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
B = chr(92)
root = "W:" + B + "DCAM" + B + "Scroll" + B + "Scroll Rescan Project"
stats = json.load(open(os.path.join(S, 'pdfstats.json')))
pdfs = [l.rstrip('\n') for l in open(os.path.join(S, 'all.txt'), encoding='utf-8') if l.lower().rstrip().endswith('.pdf')]
failed = sorted({x[0] for x in stats if x[2] < 0 and x[0] >= START and x[0] % N == K})
os.makedirs(os.path.join(S, 'done3'), exist_ok=True)
lst = open(os.path.join(S, 'pdfimg_list3_%d.tsv' % K), 'a', encoding='utf-8')

for i in failed:
    marker = os.path.join(S, 'done3', '%04d' % i)
    if os.path.exists(marker):
        continue
    path = root + pdfs[i - 1][1:].replace('/', B)
    for attempt in range(40):
        try:
            doc = pymupdf.open(path)
            break
        except Exception as e:
            if 'no such file' in str(e).lower():
                time.sleep(30)
                continue
            doc = None
            print('ERR', i, path, e, flush=True)
            break
    else:
        doc = None
        print('ERR', i, path, 'drive unavailable', flush=True)
    if doc is None:
        continue
    try:
        for pn, page in enumerate(doc, 1):
            t = page.get_text()
            with open(os.path.join(S, 'pdftext', 'p%04d_%03d.txt' % (i, pn)), 'w', encoding='utf-8') as f:
                f.write('SOURCE: %s | page %d\n' % (path, pn) + t)
            if len(t.strip()) < 300:
                zoom = min(4000 / max(page.rect.width, page.rect.height), 300 / 72)
                out = os.path.join(S, 'pdfimg', 'q%04d_%03d.png' % (i, pn))
                if not os.path.exists(out):
                    page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csGRAY).save(out)
                lst.write('q%04d_%03d\t%s\t%s | page %d\n' % (i, pn, out, path, pn))
                lst.flush()
        open(marker, 'w').close()
    except Exception as e:
        print('ERR', i, path, e, flush=True)
print('worker', K, 'done', flush=True)
