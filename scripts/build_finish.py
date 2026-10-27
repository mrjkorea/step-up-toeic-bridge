import json,re,os,copy,subprocess,glob,collections,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import overrides as OV
sys.path.insert(0,os.path.dirname(__file__)); import kparse, overrides as OV
R='/workspace/toeic-bridge'; FP=R+'/finish-pack'; PDF=R+'/build-pack/pdf'
K=json.load(open(R+'/build-pack/v2/keytree.json')); MARKS=json.load(open(FP+'/_render/marks.json'))
LV={'bas':'basic','int':'intermediate','adv':'advanced'}
KOR=re.compile(r'[\u3131-\uD7A3]')
DEF=[]; CNT=collections.Counter(); RENDER=set(); DISP=collections.Counter()
def defer(b,pid,what,why,proof=''): DEF.append((b,pid,what,why,proof))
TYS={'lc':{'bas':{'p1':[14,22,30,38],'p2':[49,55,61,67,73,79,85],'p3':[94,102,110,118,126,134]},
           'int':{'p1':[9,17,25,33],'p2':[44,50,56,62,68,74,80],'p3':[89,97,105,113,121,129]},
           'adv':{'p1':[9,17,25,33],'p2':[44,50,56,62,68,74,80],'p3':[88,94,100,107,115,123]}},
     'rc':{l:{'p4':[12,22,32,42,52,59,65,71,77],'p5':[84,90,96,102,108,114,120]} for l in LV}}
def secpages(l,sk,p,si):
    lst=TYS[sk][l][p]; t=lst[si]
    prev=lst[si-1] if si>0 else (TYS[sk][l]['p4'][-1] if p=='p5' else (TYS[sk][l]['p2'][-1] if p=='p3' else (TYS[sk][l]['p1'][-1] if p=='p2' else 0)))
    mk=[(pg,m) for pg,m in MARKS[f'{l}-{sk}'] if prev<pg<t]
    wi=[pg for pg,m in mk if m=='WI']
    st=wi[0] if wi else max(prev+2,t-6)
    return list(range(st,t)),mk
def pdir(l,sk,p,s): return f"{LV[l]}/{p}-{s}" if p=='p1' else f"{LV[l]}/{sk}-{p}-{s}"
def page_img(l,sk,p,s,pg):
    rel=f"{pdir(l,sk,p,s)}/page-{pg:03d}.png"; RENDER.add((f"{PDF}/{l}-{sk}.pdf",pg,FP+'/photos/'+rel)); return rel
# ---------- word joiner for PDF text ----------
STOP=set('a an i is at on in to of the it be by do go he me my no or so up us we am as if'.split())
def fixsp(s):
    toks=s.split(); out=[]
    for t in toks:
        if out and ((len(t)<=2 and t.lower() not in STOP and t.isalpha() and t.islower()) or (len(out[-1])==1 and out[-1].isalpha() and out[-1] not in('A','I','a') )):
            out[-1]+=t
        else: out.append(t)
    return ' '.join(out)
def pagetext(l,sk,pg): return subprocess.run(['pdftotext','-f',str(pg),'-l',str(pg),'-raw',f'{PDF}/{l}-{sk}.pdf','-'],capture_output=True,text=True).stdout.replace('니','u').replace('ᄋ','o')
# ---------- load live ----------
live={}
for f in glob.glob(FP+'/_live/data/*/*/*.json'): d=json.load(open(f)); live[d['practiceId']]=(f,d)
before={k:len(v[1]['items']) for k,v in live.items()}
NEW=collections.defaultdict(list)  # pid -> items
def add(pid,bucket,sec,**it):
    it['section']=sec; it['_b']=bucket; NEW[pid].append(it); CNT[bucket]+=1
def T(pid,b,sec,prompt,acc,**kw):
    acc=acc.strip().strip(',').strip()
    if not acc or KOR.search(acc): defer(b,pid,prompt,'answer is Korean/blank in key (English-only rule)',acc); return
    add(pid,b,sec,type='text',prompt=prompt,accept=[acc],**kw)
def C(pid,b,sec,prompt,choices,acc,**kw):
    assert acc in choices,(pid,prompt,acc,choices); add(pid,b,sec,type='choice',prompt=prompt,choices=choices,accept=acc,**kw)
# ================= A: Part I LP picture-letter =================
ALET={('bas','s01'):('bjhgadeicf','cefabd'),('bas','s02'):('cbaed','ghabkleflij'.replace('fl','f')+'' if False else 'ghabklefijdc'),
('bas','s03'):('baedgfc','cjifgehbda'),('bas','s04'):('aibgdhecf','caefgdbh'),
('int','s01'):('deajibchfg','gafhcbed'),('int','s02'):('efcgbad','aedcfhbg'),('int','s03'):('cefbdahg','cedihjfbga'),('int','s04'):('abcidghef','eabfigcdh'),
('adv','s01'):('bgehafcd','dagfhcbie'),('adv','s02'):('hbfaecdg','bfgidache'),('adv','s03'):('gafbdhcei','beagcdf'),('adv','s04'):('dafebcgh','cahfegijbd')}
ADV2={'lp1':["The children are playing on the slide.","The children are playing on the swings.","The boy is playing in the sand.","The boy is climbing the tree.","The boy is climbing the fence.","The boy is leaning against the fence.","The girls are on the seesaw.","The children are in the jungle gym."],
'lp2':["The children are swimming in the ocean.","The man is running along the beach.","The man is walking his dog along the beach.","The man is lying on the beach.","They are sitting under beach umbrellas.","They are having a barbecue.","They are setting up the tent.","They are building a sandcastle.","They are feeding the seagulls."]}
def sentences(l,s,b):
    if l=='adv' and s=='s02': return ADV2[b]
    if l=='int': return None
    txt=' '.join(K[l]['ans']['p1'][s][b])
    if l=='bas':
        parts=re.split(r'\s*-?\s*\b[a-l]\b\s*/?',txt)  # rough
        return None
    sents=re.findall(r'\d+\.\s*(.+?)\s*/?\s*\b[a-l]\b\.?(?=\s*\d+\.|\s*$)',txt)
    return sents
pidmap={}
for (l,s),(l1,l2) in ALET.items():
    pid=f'{l}-lc-p1-{s}'; si=int(s[1:])-1; pages,mk=secpages(l,'lc','p1',si)
    lpp=[pg for pg,m in mk if m=='LP']
    for bi,(b,lets) in enumerate((('lp1',l1),('lp2',l2))):
        sec=f'Listening Practice {bi+1}'; img=page_img(l,'lc','p1',s,lpp[bi])
        mx=max(lets); ch={c:c for c in 'abcdefghijkl' if c<=mx}
        assert len(set(lets))==len(lets),(l,s,b)
        sents=sentences(l,s,b)
        for n,ch_ in enumerate(lets,1):
            C(pid,'A',sec,f'{sec} — statement {n}: listen and choose the letter of the matching picture.',{k.upper():v for k,v in ch.items()},ch_.upper(),audioOnly=True,photo=img)
        if l=='adv':
            if not sents or len(sents)!=len(lets): defer('A',pid,b+' dictation','sentence count mismatch in key',str(sents)); continue
            for n,se in enumerate(sents,1): T(pid,'A',sec,f'{sec} — statement {n}: type the sentence you hear.',se,audioOnly=True,photo=img)
# ================= B: Part II LP part 2 dictation =================
P2FIX={('int','s01'):{1:'visit your grandmother / I didn\'t / my grandmother',4:'sisters / only child / My sister'},('int','s04'):{1:'birthday / birthday gift'},
('int','s07'):{1:'having some coffee / thirsty / good idea / tea'},('bas','s02'):{1:'doing / cleaning'},('bas','s07'):{1:'math test / difficult'}}
ADVP2LP={'s02':{(2,4):'(A)/On my birthday.'},'s03':{(1,4):'(B)/Which one of the apartments',(2,1):'(A)/The latest cell phone will.',(2,2):'(A)/Go up 1st Avenue.'}}
for l in LV:
  for s in sorted(K[l]['ans']['p2']):
    pid=f'{l}-lc-p2-{s}'; si=int(s[1:])-1; pages,mk=secpages(l,'lc','p2',si)
    lp=[pg for pg,m in mk if m=='LP']; img=page_img(l,'lc','p2',s,lp[0] if lp else pages[-2])
    txt=' '.join(K[l]['ans']['p2'][s]['lp'])
    m=re.search(r'2\.\s*(1\).*)$',txt); body=m.group(1) if m else ''
    subs=dict((int(a),b.strip()) for a,b in re.findall(r'(\d)\)\s*(.*?)(?=\s*\d\)|$)',body))
    if l=='adv':
        p1=re.search(r'1\.\s*(1\).*?)\s2\.\s',txt).group(1); s1=dict((int(a),b.strip()) for a,b in re.findall(r'(\d)\)\s*(.*?)(?=\s*\d\)|$)',p1))
        for part,d in ((1,s1),(2,subs)):
            for n in range(1,5):
                v=ADVP2LP.get(s,{}).get((part,n),d.get(n,''))
                mm=re.match(r'\(([ABC])\)\s*/?\s*(.*)$',v)
                if not mm: defer('B',pid,f'LP {part}.{n}','key unreadable',v); continue
                if part==2: C(pid,'B','Listening Practice',f'Listening Practice 2-{n}): choose the best response.',{'A':'(A)','B':'(B)','C':'(C)'},mm.group(1),audioOnly=True,photo=img)
                if mm.group(2).strip(): T(pid,'B','Listening Practice',f'Listening Practice {part}-{n}): type the words you hear in the blank.',mm.group(2).strip().rstrip('.') if False else mm.group(2).strip(),audioOnly=True,photo=img)
        continue
    subs.update(P2FIX.get((l,s),{}))
    for n in range(1,5):
        v=subs.get(n)
        if not v: defer('B',pid,f'LP 2-{n}','missing in key',txt); continue
        segs=[x.strip() for x in v.split('/') if x.strip()]
        for j,sg in enumerate(segs,1): T(pid,'B','Listening Practice',f'Listening Practice 2-{n}) blank {j}: type the words you hear.',sg,audioOnly=True,photo=img)
# adv Warm-Up 2 (and s03 Warm-Up 1)
ADVWU1_S03=['Which swimsuit do you like','Which way does the tour bus','Which way do I go to get to','Which room would you like to','Which car is yours?']
for s in sorted(K['adv']['ans']['p2']):
    pid=f'adv-lc-p2-{s}'; si=int(s[1:])-1; pages,mk=secpages('adv','lc','p2',si)
    wu=[pg for pg,m in mk if m=='WU']; img=page_img('adv','lc','p2',s,wu[0] if wu else pages[1])
    txt=' '.join(K['adv']['ans']['p2'][s]['warmup'])
    if s=='s03':
        for i,a in enumerate(ADVWU1_S03): T(pid,'B','Warm-Up',f'Warm-Up 1-({"abcde"[i]}): type the words you hear.',a,audioOnly=True,photo=img)
    p2=txt[txt.index('2. (a)')+3:]
    it=re.findall(r'\(([a-e])\)\s*(.*?)(?=\s*\([a-e]\)|$)',p2)
    for let,v in it:
        segs=[x.strip() for x in v.split('/') if x.strip()]
        for j,sg in enumerate(segs,1):
            T(pid,'B','Warm-Up',f'Warm-Up 2-({let}) part {j}: type the words you hear.',sg,audioOnly=True,photo=img)
# adv P1 Check-Up (2) part 2 paraphrase
PARA={'s01':[('repair a car','fix a car'),('use a drill','drill'),('talk on the phone','answer the phone'),('conduct traffic','direct traffic'),('have a meeting','talk in a group')],
's02':[('make an order','order'),('fix the road','pave the road'),('fix a car','work on the car'),('take a seat','sit'),('make hamburgers','cook hamburgers')],
's03':[('come down','descend'),('give a speech','give a presentation'),('boat','paddle the boat'),('touch the animal','pet the animal'),('cook the food','make the food')],
's04':[('go up the stairs','go up the steps'),('write down something','take notes'),('film','take a picture'),('give food','serve food'),('board the train','get on the train')]}
for s,pr in PARA.items():
    pid=f'adv-lc-p1-{s}'; pages,mk=secpages('adv','lc','p1',int(s[1:])-1); img=page_img('adv','lc','p1',s,pages[-1])
    for i,(a,b) in enumerate(pr): T(pid,'B','Check-Up (2)',f'Check-Up 2-({"abcde"[i]}): listen and type the expression that means the same as “{a}”.',b,audioOnly=True,photo=img)
# ================= C: garbled keys =================
pg=secpages('int','lc','p1',2)[0]
for i,a in enumerate(['a lot of trees','a lot of cars','a lot of people','on the table','on the floor']):
    C('int-lc-p1-s03','C','Check-Up',f'Check-Up ({"abcde"[i]}): choose the words you hear.',{'A':'a lot of cars','B':'a lot of people','C':'a lot of trees','D':'on the floor','E':'on the table'},{'a lot of cars':'A','a lot of people':'B','a lot of trees':'C','on the floor':'D','on the table':'E'}[a],audioOnly=True,photo=page_img('int','lc','p1','s03',pg[-1]))
C3=[('bas-lc-p3-s01','Listening Practice 1','(a)','Who is the man?' ,'baker'),('bas-lc-p3-s01','Listening Practice 3','(a)','When?','At 9:00'),
    ('int-lc-p3-s03','Listening Practice 1','(a)','When?','At five'),('adv-lc-p3-s01','Listening Practice 1','(a)','Where?','In a bank')]
for pid,sec,lab,_,a in C3: T(pid,'C',sec,f'{sec} {lab}: listen and type the final answer.',a,audioOnly=True)
for i,a in enumerate(['Take out all electronic devices','On a bus','Move the car'],1): T('adv-lc-p3-s05','C','Warm-Up',f'Warm-Up {i}: listen and type the answer.',a,audioOnly=True)
for i,a in enumerate(['z','z','dʒ']): C('bas-lc-p2-s06','C','Pronunciation Check-Up',f'Pronunciation Check-Up 2-({"abc"[i]}): choose the sound you hear.',{'A':'z','B':'dʒ'},{'z':'A','dʒ':'B'}[a],audioOnly=True)
for i,a in enumerate(['θ','ð','θ']): C('bas-lc-p2-s07','C','Pronunciation Check-Up',f'Pronunciation Check-Up 1-({"abc"[i]}): choose the sound you hear.',{'A':'θ','B':'ð'},{'θ':'A','ð':'B'}[a],audioOnly=True)
# ================= G (part): Part III LP dictation blanks =================
for l in LV:
  for s,bl in K[l]['ans']['p3'].items():
    if s=='at': continue
    pid=f'{l}-lc-p3-{s}'; si=int(s[1:])-1; pages,mk=secpages(l,'lc','p3',si); lps=[pg for pg,m in mk if m=='LP']
    for bi,b in enumerate([x for x in ('lp1','lp2','lp3') if x in bl]):
        sec=f'Listening Practice {bi+1}'; img=page_img(l,'lc','p3',s,lps[bi] if bi<len(lps) else pages[-1])
        txt=' '.join(bl[b])
        if (l,s,b)==('adv','s01','lp1'): txt='(a) apply for a loan / checking account / In a bank (b) have an appointment / take the elevator / At a hospital'
        parts=re.findall(r'\(([ab])\)\s*(.*?)(?=\s*\([ab]\)|$)',txt)
        if len(parts)<2: defer('G',pid,sec+' dictation','key OCR lost the (a)/(b) markers; finals already live',txt); continue
        for let,v in parts:
            segs=[x.strip() for x in v.split('/') if x.strip()][:-1]
            for j,sg in enumerate(segs,1): T(pid,'G',sec,f'{sec} ({let}) blank {j}: type the words you hear.',sg,audioOnly=True,photo=img)
# ================= I: Words & Idioms Check-Up; G: RC warmup/gp/vp; G: RP =================
def emit(pid,bucket,sec,spec,img):
    k=spec[0]
    if k=='C':
        _,lab,q,opts,ans=spec; keys=[chr(65+i) for i in range(len(opts))]
        C(pid,bucket,sec,f'{sec} {lab}: {q}',dict(zip(keys,opts)),keys[opts.index(ans)],photo=img)
    elif k=='T':
        _,lab,q,acc=spec; add(pid,bucket,sec,type='text',prompt=f'{sec} {lab}: {q}',accept=acc,photo=img)
    else:
        _,lab,q=spec; DISP[bucket]+=1; add(pid,bucket,sec,type='display',displayOnly=True,scored=False,prompt=f'{sec} {lab}: {q}',pageImage=img,photo=img)
def generic(l,sk,p,s,b,bucket,sec,img,pid):
    if (pid,b) in OV.OVR:
        for spec in OV.OVR[(pid,b)]:
            if spec[0]=='BANK':
                _,bank,labs=spec; srt=sorted(bank,key=str.lower); keys=[chr(65+i) for i in range(len(srt))]
                for lab,a in zip(labs,bank): C(pid,bucket,sec,f'{sec} {lab}: choose the word or phrase that completes the sentence (see the book page).',dict(zip(keys,srt)),keys[srt.index(a)],photo=img)
            else: emit(pid,bucket,sec,spec,img)
        return
    lines=K[l]['ans'][p][s][b]; items,probs=kparse.parse(lines)
    raw=' '.join(lines)
    if KOR.search(raw) and not items:
        emit(pid,bucket,sec,('D','vocabulary','Study the vocabulary table on the book page (Korean meaning - English word). Not scored.'),img); return
    seen=set(); bad=[x for x in probs if x.startswith('text before') or x.startswith('no markers')]
    for n,sb,a in items:
        if (n,sb) in seen: bad.append(f'duplicate {n}{sb}')
        seen.add((n,sb))
    if bad: defer(bucket,pid,sec,'answer-key OCR scrambled: '+'; '.join(bad),raw[:200]); return
    ok=[]
    for n,sb,a in items:
        lab=(f'{n}-' if n else '')+(sb or '')
        a=re.sub(r'\s+I$','',a.strip()); a=re.sub(r'\s*-Up\s*[|I]?\s*Warm.*$','',a)
        hit=[v for (kp,ks,kl),v in OV.PATCH.items() if kp==pid and kl==lab and (ks==sec or ks.startswith(sec+' '))]
        if hit:
            for spec in hit[0]: emit(pid,bucket,sec,spec,img)
            continue
        m=re.fullmatch(r"([A-Za-z]+)\s*(?:-|→)?\s+([A-Za-z]+)",a)
        if m and m.group(1).lower()!=m.group(2).lower() and m.group(1)[:3].lower()==m.group(2)[:3].lower() and not m.group(2).endswith('st'):
            add(pid,bucket,sec,type='text',prompt=f'{sec} {lab}: correct the wrong word (see the book page).',accept=[m.group(2)],photo=img); continue
        w=a.split()
        if len(w)>=2 and len(w)%2==0 and w[:len(w)//2]==w[len(w)//2:]: a=' '.join(w[:len(w)//2])
        if re.search(r'\w-\w',a) and ' ' not in a and b!='words-checkup' and not re.search(r'(first|second|third|[a-z]+ty)-',a) and (lambda x,y: x[:4].lower()==y[:4].lower())(*a.split('-',1)): defer(bucket,pid,f'{sec} {lab}','key shows a word pair joined by a dash (two-blank answer); split ambiguous',a); continue
        MAN={"Jane cannot/ can not/ can't speak Korea.":["Jane cannot speak Korea.","Jane can not speak Korea.","Jane can't speak Korea."],"Sam will not/ won't go to see his aunt tomorrow.":["Sam will not go to see his aunt tomorrow.","Sam won't go to see his aunt tomorrow."]}
        if a in MAN: add(pid,bucket,sec,type='text',prompt=f'{sec} {lab}: rewrite the sentence as shown in the book (see the book page).',accept=MAN[a],photo=img); continue
        if not a or re.search(r'Test Your|Warm|Check|Up\b|\d\.\(',a) or len(a.split())>14: defer(bucket,pid,f'{sec} {lab}','key text empty/garbled',a); continue
        ok.append((lab,a))
    if b=='words-checkup' and len(ok)>=2 and all(len(a.split())<=4 and '/' not in a and not KOR.search(a) for _,a in ok):
        bank=sorted(set(a for _,a in ok),key=str.lower); keys=[chr(65+i) for i in range(len(bank))]; ch=dict(zip(keys,bank))
        for lab,a in ok: C(pid,bucket,sec,f'{sec} {lab}: choose the word or phrase that completes the sentence (see the book page).',ch,keys[bank.index(a)],photo=img)
        return
    for lab,a in ok:
        if re.fullmatch(r'\(?[a-dA-D]\)?',a.strip()):
            L=a.strip('() ').upper(); C(pid,bucket,sec,f'{sec} {lab}: choose the answer (see the book page).',{'A':'(a)','B':'(b)','C':'(c)','D':'(d)'},L,photo=img); continue
        if a.strip() in('T','F'): C(pid,bucket,sec,f'{sec} {lab}: true or false?',{'A':'True','B':'False'},'A' if a.strip()=='T' else 'B',photo=img); continue
        if '/' in a and b not in('words-checkup',):
            alts=[x.strip() for x in a.split('/') if x.strip()]
            if alts and all(len(x.split())==1 for x in alts):
                if KOR.search(a): defer(bucket,pid,f'{sec} {lab}','Korean',a); continue
                add(pid,bucket,sec,type='text',prompt=f'{sec} {lab}: type the answer (see the book page).',accept=alts,photo=img); continue
            defer(bucket,pid,f'{sec} {lab}','key gives a multi-word alternative set that cannot be split into exact accepts without guessing',a); continue
        T(pid,bucket,sec,f'{sec} {lab}: type the answer (see the book page).',a,photo=img)
SECN={'words-checkup':'Words and Idioms Check-Up','warmup':'Warm-Up','gp':'Grammar Practice','vp':'Vocabulary Practice'}
for l in LV:
  for p in ['p1','p2','p3','p4','p5']:
    sk='lc' if p<'p4' else 'rc'
    for s,bl in K[l]['ans'][p].items():
      if s=='at': continue
      pid=f'{l}-{sk}-{p}-{s}'
      if pid not in live: defer('G',pid,'whole section','no live practice json',''); continue
      si=int(s[1:])-1; pages,mk=secpages(l,sk,p,si)
      def mpage(kind,idx=0):
          x=[pg for pg,m in mk if m==kind]; return x[idx] if len(x)>idx else None
      for b in bl:
        if b=='words-checkup': generic(l,sk,p,s,b,'I',SECN[b],page_img(l,sk,p,s,mpage('WI') or pages[0]),pid)
        elif sk=='rc' and b in('warmup','gp','vp'): generic(l,sk,p,s,b,'G',SECN[b],page_img(l,sk,p,s,(mpage('WU') if b=='warmup' else mpage('LP')) or pages[1]),pid)
# RP from PDF text
def ocrtext(l,pg):
    c=f'{FP}/_render/ocr-{l}-rc-{pg}'
    if not os.path.exists(c+'.txt'):
        subprocess.run(['pdftoppm','-f',str(pg),'-l',str(pg),'-r','250','-png','-singlefile',f'{PDF}/{l}-rc.pdf',c],check=True)
        subprocess.run(['tesseract',c+'.png',c],capture_output=True)
    return open(c+'.txt').read()
def rp_questions(l,pg):
    t=pagetext(l,'rc',pg)
    o=ocrtext(l,pg)
    if 'Reading Practice' not in t+o: return {}
    if re.search(r'\(a\)',o):
        o=o.replace('Ata ','At a ')
        if not re.search(r'Reading Practice\s*[12]',o):
            hd=re.findall(r'Reading Practice\s*([12])',t)
            ch=re.split(r'(?m)(?=^\s*1\s*\.\s)',o)[1:]
            if hd and len(ch)>=len(hd): o=''.join(f'Reading Practice {h}\n'+c for h,c in zip(hd,ch[-len(hd):]))
        if re.search(r'Reading Practice\s*[12]',o): t=o
    for m in re.finditer(r'Reading Practice\s*([12])',t): pass
    segs=re.split(r'Reading Practice\s*([12])',t)
    out={}
    for i in range(1,len(segs),2):
        body=segs[i+1]; qs=[]
        for qm in re.finditer(r'(?m)^\s*([12])\s*\.\s*(.+?)\n(.*?)(?=^\s*[12]\s*\.\s|\Z)',body,re.S):
            opts=re.findall(r'\(([a-d])\)\s*(.+)',qm.group(3))
            qs.append((qm.group(2).strip(),[(a,o.strip()) for a,o in opts]))
        out.setdefault(int(segs[i]),qs)
    return out
for l in LV:
  for s,bl in K[l]['ans']['p5'].items():
    if s=='at': continue
    pid=f'{l}-rc-p5-{s}'; pages,mk=secpages(l,'rc','p5',int(s[1:])-1)
    found={}
    for pg in pages:
        for k,v in rp_questions(l,pg).items():
            if v and k not in found: found[k]=(pg,v)
    for k in (1,2):
        b=f'rp{k}'; sec=f'Reading Practice {k}'
        if b not in bl: defer('G',pid,sec,'key block missing',''); continue
        keys=re.findall(r'(\d)\.\s*\(([a-d])\)',' '.join(bl[b]))
        if k not in found: defer('G',pid,sec,'question text not extractable from PDF text layer','');continue
        pg,qs=found[k]
        if (l,s,k)==('bas','s06',2): qs=[('What is this list for?',[('a','For shopping'),('b','For cooking')]),('How many items does the writer need?',[('a','4'),('b','5')])]
        img=page_img(l,'rc','p5',s,pg)
        for n,let in keys:
            n=int(n)
            if n>len(qs) or not qs[n-1][1]: defer('G',pid,f'{sec} {n}','question/options not parsed from page text',str(qs)[:200]); continue
            q,opts=qs[n-1]; ch={o[0].upper():o[1] for o in opts}
            if let.upper() not in ch or any(KOR.search(v) for v in ch.values()): defer('G',pid,f'{sec} {n}','options incomplete',str(opts)); continue
            C(pid,'G',sec,q,ch,let.upper(),passageImage=img)
# ================= H: Pronunciation listen & repeat (basic only; lists read from page text + page images 25, 94) =================
HW={('p1','s01',('lc',None)):None}
HL=[('p1','s01','vase vet vest vanilla base bet best bench'),('p1','s02','flower fond fool face place pond pool pace'),
('p1','s03','lace leaf little long race ready ribbon rope'),('p2','s01','soon sea six sister zoo zebra zipper zero'),
('p2','s02','zipper zebra zoo zone page large village courage'),('p2','s03','church bench chair fish brush share'),
('p2','s04','three think thank this that mother'),('p2','s05','bomb climb comb knee knife know'),
('p3','s01','clean up|put on|get off|turn off|turn on|take off'),('p3','s02','want to|like to|wait to|closed to|help me|next to'),
('p3','s03','better letter writer butter'),('p3','s04',"dock|can't|director|box|car")]
for p,s,ws in HL:
    pid=f'bas-lc-{p}-{s}'; pages,mk=secpages('bas','lc',p,int(s[1:])-1)
    pgn={('p1','s03'):25,('p3','s01'):89}.get((p,s),pages[0]); img=page_img('bas','lc',p,s,pgn)
    words=ws.split('|') if '|' in ws else ws.split()
    for i,w in enumerate(words,1): add(pid,'H','Pronunciation',type='text',prompt=f'Pronunciation — Listen and Repeat #{i}: say it aloud, then type the word or phrase you hear.',accept=[w],audioOnly=True,photo=img)
# ================= D: truncated choices =================
DFIX=[('int-rc-at','100',{'A':"Soap operas are more popular than nature programs.",'B':"Sports programs are more popular than comedy programs.",'C':"Comedy programs are less popular than soap operas.",'D':"Sports programs are more popular than soap operas."}),
('adv-rc-at','83',{'C':"Her children have an important math exam soon."}),('adv-rc-at','96',{'C':"Take cameras into school",'D':"Shaking hands with the King and Queen"})]
ORDER=['Words and Idioms Check-Up','Pronunciation','Pronunciation Check-Up','Warm-Up','Listening Practice','Listening Practice 1','Listening Practice 2','Listening Practice 3','Grammar Practice','Vocabulary Practice','Reading Practice 1','Reading Practice 2','Check-Up','Check-Up (2)','Test Your Skills']
out={}
for pid,(f,d) in live.items():
    d=copy.deepcopy(d); items=d['items']
    for pref,lab,ch in DFIX:
        if pid.startswith(pref):
            for it in items:
                if it.get('label')==lab: it['choices'].update(ch); CNT['D']+=1
    if pid=='int-lc-p2-s07':
        for it in items:
            if it.get('section')=='Check-Up' and it['choices'].get('B')=='used my computer.':
                it['choices']['B']='I used my computer.'; CNT['D']+=1
    new=NEW.get(pid,[])
    for i,it in enumerate(items): it['_k']=(ORDER.index(it.get('section')) if it.get('section') in ORDER else 99,0,i)
    for i,it in enumerate(new): it['_k']=(ORDER.index(it['section']),1,i)
    allit=sorted(items+new,key=lambda x:x['_k'])
    for n,it in enumerate(allit,1):
        it.pop('_k',None); it.pop('_b',None); it['id']=f'q{n}'
        if 'label' not in it or it in new or True: pass
    for it in allit:
        if 'label' not in it: it['label']=it['id'][1:]
    # relabel only lc section items numerically (RC AT keep book numbers)
    if '-at-' not in pid:
        for it in allit: it['label']=it['id'][1:]
    d['items']=allit
    pages=None
    m=re.match(r'(bas|int|adv)-(lc|rc)-(p\d)-(s\d\d)$',pid)
    if m:
        l,sk,p,s=m.groups(); pg,_=secpages(l,sk,p,int(s[1:])-1); d['bookPages']=[page_img(l,sk,p,s,x) for x in pg]
    # E: passage images
    for it in allit:
        if it.get('passagePage') and 'passageImage' not in it:
            l=pid[:3]; pp=it['passagePage']; rel=f"{LV[l]}/rc-pages/page-{pp:03d}.png"; RENDER.add((f'{PDF}/{l}-rc.pdf',pp,FP+'/photos/'+rel)); it['passageImage']=rel; CNT['E']+=1
    if pid in NEW or d['items']!=live[pid][1]['items']: d['contentVersion']='v4-finishpack-2026-10-28'
    out[pid]=(f.replace('/_live/data/','/data/'),d)
# F: Warm-Up photos (Part I)
for pid,(f,d) in out.items():
    if re.match(r'(bas|int|adv)-lc-p1-s0\d$',pid):
        l=pid[:3]; s=pid[-3:]; pg,mk=secpages(l,'lc','p1',int(s[1:])-1); wu=[x for x,mm in mk if mm=='WU']; wp=wu[0] if wu else pg[1]
        img=page_img(l,'lc','p1',s,wp)
        for it in d['items']:
            if it.get('section')=='Warm-Up' and 'photo' not in it: it['photo']=img; CNT['F']+=1
for f,d in out.values(): os.makedirs(os.path.dirname(f),exist_ok=True); json.dump(d,open(f,'w'),ensure_ascii=False,indent=1)
# render
for pdf,pg,dst in sorted(RENDER):
    if os.path.exists(dst): continue
    os.makedirs(os.path.dirname(dst),exist_ok=True); subprocess.run(['pdftoppm','-f',str(pg),'-l',str(pg),'-r','100','-png','-singlefile',pdf,dst[:-4]],check=True)
json.dump({'counts':CNT,'deferred':DEF,'before':before,'after':{k:len(v[1]['items']) for k,v in out.items()},'renders':len(RENDER),'display':DISP},open(FP+'/_build_state.json','w'),ensure_ascii=False,indent=1)
print(CNT,len(DEF),len(RENDER))
