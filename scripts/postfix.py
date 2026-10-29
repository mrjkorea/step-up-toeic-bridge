# Post-build fixes read from key images (arrow "wrong -> right" lost in PDF text layer). Run after build_finish.py.
import json,glob,os
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data')
F={('bas-rc-p4-s05','Grammar Practice 4-(b)'):['are'],('bas-rc-p4-s05','Grammar Practice 4-(c)'):['Those'],
 ('adv-rc-p4-s03','Warm-Up 3-(b)'):['is'],('adv-rc-p4-s03','Grammar Practice 4-(c)'):['arrives'],('adv-rc-p4-s03','Grammar Practice 5-(a)'):['belongs'],('adv-rc-p4-s03','Grammar Practice 5-(d)'):['is'],
 ('adv-rc-p4-s01','Grammar Practice 3-(a)'):['of'],('adv-rc-p4-s01','Grammar Practice 5-(b)'):['to return'],
 ('int-rc-p4-s04','Warm-Up 3-(b)'):['fast'],('int-rc-p4-s05','Warm-Up 1-(d)'):['easier - easiest','easier, easiest','easier easiest'],
 ('int-rc-p4-s05','Warm-Up 1-(e)'):['more wonderful - most wonderful','more wonderful, most wonderful','more wonderful most wonderful'],
 ('adv-rc-p4-s06','Vocabulary Practice 2-(a)'):['touch - rock','touch, rock','touch rock','touch / rock'],
 ('adv-rc-p4-s06','Vocabulary Practice 2-(b)'):['taste - chocolate','taste, chocolate','taste chocolate','taste / chocolate'],
 ('adv-rc-p4-s06','Vocabulary Practice 2-(c)'):['smell - perfume','smell, perfume','smell perfume','smell / perfume'],
 ('adv-rc-p4-s06','Vocabulary Practice 2-(d)'):['feel - excited','feel, excited','feel excited','feel / excited'],
 ('adv-rc-p4-s09','Vocabulary Practice 2-(a)'):['department store'],
 ('adv-rc-p4-s09','Vocabulary Practice 2-(b)'):['movie theater'],
 ('adv-rc-p4-s09','Vocabulary Practice 2-(c)'):['post office'],
 ('adv-rc-p4-s09','Vocabulary Practice 2-(d)'):['parking lot'],
 ('int-rc-p4-s06','Vocabulary Practice 2-(a)'):['baseball player']}
DROP={('int-rc-p4-s05','Warm-Up 2-(b)')}  # duplicate of hand-built 2-(b)
ADD={('int-rc-p4-s05','Warm-Up 1-(e)'):{'type':'text','prompt':'Warm-Up 1-(f): write the comparative and superlative forms (see the book page).','accept':['hotter - hottest','hotter, hottest','hotter hottest'],'label':'1-(f)'}}
n=0
for f in glob.glob(D+'/*/*/*.json'):
  pid=os.path.basename(f)[:-5]; j=json.load(open(f)); out=[]
  for i in j['items']:
    k=next(((p,s) for (p,s) in list(F)+list(DROP) if p==pid and i.get('prompt','').startswith(s+':')),None)
    if k in DROP and i.get('accept')==['better']: n+=1; continue
    if k in F: i['accept']=F[k]; i['prompt']=k[1]+': correct or complete it (see the book page).'; n+=1
    out.append(i)
    if k in ADD: x=dict(i); x.update(ADD[k]); out.append(x); n+=1
  for q,i in enumerate(out,1):
    i['id']=f'q{q}'
    # Preserve book-faithful item labels (Zap method); only assign id for form keys.
  j['items']=out
  if 'count' in j: j['count']=len(out)
  json.dump(j,open(f,'w'),ensure_ascii=False,indent=1)
print('postfix',n)
