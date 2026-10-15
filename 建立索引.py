from pathlib import Path
import os,json,hashlib,datetime,re
BASE=Path(__file__).resolve().parent
DATA=BASE/'数据'
ROOT=Path(os.environ.get('FOOTAGE_ROOT',str(BASE/'素材'))).resolve()
def build():
 if not ROOT.is_dir():raise RuntimeError('请设置 FOOTAGE_ROOT 指向已授权的素材目录')
 DATA.mkdir(exist_ok=True)
 old=json.loads((DATA/'素材索引.json').read_text()) if (DATA/'素材索引.json').exists() else {'products':[],'recordings':[]}
 known={r['path']:r for r in old['recordings']}
 for p in ROOT.rglob('*'):
  if not p.is_file() or p.suffix.lower() not in ['.mp4','.mov','.mkv','.m4v'] or str(p) in known:continue
  m=re.search(r'(20\d{2})[.\-](\d{1,2})[.\-](\d{1,2})',p.name)
  if not m:continue
  try:date=datetime.date(*map(int,m.groups())).isoformat()
  except ValueError:continue
  key='M-'+hashlib.sha256(str(p).encode()).hexdigest()[:16]
  old['recordings'].append({'id':key,'name':p.name,'path':str(p),'date':date,'kind':'原始回放','bytes':p.stat().st_size,'status':'待补充产品','product_ids':[],'analysis':[]})
 old.update(updated_at=datetime.datetime.now().astimezone().isoformat(),source_root=str(ROOT),stats={'raw_recordings':len(old['recordings']),'slices':0,'raw_with_products':sum(bool(r['product_ids']) for r in old['recordings'])})
 (DATA/'素材索引.json').write_text(json.dumps(old,ensure_ascii=False,indent=2))
 return old
