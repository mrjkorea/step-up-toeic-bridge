import json,re,collections as C
B="https://mrjkorea.github.io/step-up-toeic-bridge/"
cat=json.load(open('data/catalog.json'))
BOOK={'basic-lc':'bas-lc','basic-rc':'bas-rc','intermediate-lc':'int-lc','intermediate-rc':'int-rc','advanced-lc':'adv-lc','advanced-rc':'adv-rc'}
fails=[];warns=[];inv={};cv=C.Counter();photos=set()
LET=re.compile(r'^\(?[A-Za-z]\)?\.?$')
CAP=re.compile(r'^\([A-E]\)$')
STUB=re.compile(r'\bTODO\b|DEFERRED|see (the )?(book|page|textbook)|\[blank\]|placeholder|lorem|^…$|^\.\.\.$|page-\d+\.(png|jpg)',re.I)
def add(L,b,pid,it,pat,ex):L.append(dict(book=b,practiceId=pid,itemIdOrLabel=f"{it.get('id')} / {it.get('label')} [{it.get('section','')}]",pattern=pat,excerpt=ex[:300],url=B+'#/practice/'+pid))
for t in cat['tracks']:
  b=BOOK[t['trackId']];np=ni=0
  for p in t['practices']:
    pid=p['id'];d=json.load(open(p['dataPath']));np+=1;cv[d.get('contentVersion')]+=1
    raw=json.dumps(d,ensure_ascii=False)
    for m in set(re.findall(r'[\w/.-]*page-\d+\.(?:png|jpg)',raw)): add(fails,b,pid,{},'page-image-ref',m)
    if p.get('stub') or d.get('stub'): add(fails,b,pid,{},'stub-practice','stub true')
    if not d.get('items'): add(fails,b,pid,{},'no-items','')
    for it in d.get('items',[]):
      ni+=1
      if it.get('photo'): photos.add(it['photo'])
      ty=it.get('type');pr=(it.get('prompt') or '').strip();st=(it.get('stem') or '').strip()
      for s in [pr,st,str(it.get('passage') or ''),str(it.get('passageHead') or '')]:
        if STUB.search(s): add(fails,b,pid,it,'placeholder/see-book',s)
      if ty=='display': continue
      if not pr and not st: add(fails,b,pid,it,'empty-stem',json.dumps(it,ensure_ascii=False))
      if 'stem' in it and not st: add(fails,b,pid,it,'empty-stem-field',pr)
      if re.search(r'true|false|\bT/F\b',pr+st,re.I) or (ty=='choice' and set(map(str.lower,map(str,(it.get('choices') or {}).values())))<= {'true','false','t','f'} and it.get('choices')):
        body=re.sub(r'^.*?:\s*','',st or pr).strip()
        if not st and (re.search(r'Is it True or False\??$',pr) or len(re.sub(r'\(T/F\)','',body).strip())<8): add(fails,b,pid,it,'tf-empty-statement',pr)
      a=it.get('accept')
      if ty!='display' and (a is None or a=='' or a==[] or (isinstance(a,list) and not any(str(x).strip() for x in a))): add(fails,b,pid,it,'missing-accept',pr)
      if ty=='choice':
        ch=it.get('choices') or {}
        if not ch: add(fails,b,pid,it,'no-choices',pr)
        vals=[str(v).strip() for v in ch.values()]
        if any(not v for v in vals): add(fails,b,pid,it,'empty-choice',json.dumps(ch,ensure_ascii=False))
        if vals and all(CAP.match(v) for v in vals): add(fails,b,pid,it,'bare-(A)(B)(C)-choices-no-english',(pr+' '+st).strip()+' | '+json.dumps(ch,ensure_ascii=False)+(' [photo]' if it.get('photo') else ''))
        elif vals and all(LET.match(v) for v in vals) and re.search(r'\(a\).+\(b\)',pr+st): add(warns,b,pid,it,'letter-choices-options-in-stem (book format, stands alone)',pr[:200])
        elif vals and all(LET.match(v) for v in vals):
          if it.get('photo'): add(warns,b,pid,it,'letter-only-choices-with-photo (picture-label match)',pr+' | '+json.dumps(ch))
          elif 'Pronunciation' in pr: add(warns,b,pid,it,'phoneme-letter-choices (b/v, f/p, s/z — legit sound contrast)',pr+' | '+json.dumps(ch))
          else: add(fails,b,pid,it,'letter-only-choices-no-english',pr+' '+st+' | '+json.dumps(ch,ensure_ascii=False))
        if len(set(vals))<len(vals): add(fails,b,pid,it,'duplicate-choices',json.dumps(ch,ensure_ascii=False))
        if isinstance(a,str) and a not in ch: add(fails,b,pid,it,'accept-not-in-choices',f'accept={a} choices={list(ch)}')
        if isinstance(a,list) and any(x not in ch for x in a): add(fails,b,pid,it,'accept-not-in-choices',f'accept={a}')
        if not st and not it.get('audioOnly') and not it.get('passage') and not it.get('photo') and len(pr)<40 and not re.search(r'_{2,}',pr):
          add(warns,b,pid,it,'short-standalone-choice-prompt',pr+' | '+json.dumps(ch,ensure_ascii=False)[:150])
      if ty=='text' and not it.get('audioOnly') and not st and not it.get('passage') and (re.search(r'Fill in the blank\.?$',pr) or not re.search(r'_{2,}|\w{3,} \w{3,} \w{3,}|Write .+ in words|Combine:',pr)):
        add(fails,b,pid,it,'text-item-no-standalone-content',pr)
  inv[b]=(np,ni)
json.dump(dict(inv=inv,cv=dict(cv),fails=fails,warns=warns,photos=sorted(photos)),open('sweep_out.json','w'),ensure_ascii=False,indent=1)
print(len(fails),len(warns))
print(C.Counter((f['book'],f['pattern']) for f in fails))
