from pathlib import Path
import json,datetime
DATA=Path(__file__).resolve().parent/'数据';FILE=DATA/'产品筛选.json'
def state():
 try:return json.loads(FILE.read_text())
 except (OSError,ValueError):return {'deleted':{},'edits':{}}
def write(s):
 tmp=FILE.with_suffix('.tmp');tmp.write_text(json.dumps(s,ensure_ascii=False,indent=2));tmp.replace(FILE)
def hidden():return state().get('deleted',{})
def change(pid,products,restore=False):return bulk([pid],products,'restore' if restore else 'delete')
def bulk(ids,products,action,category=''):
 if not isinstance(ids,list) or not ids or len(ids)>3000:raise ValueError('请选择要处理的产品')
 ids=list(dict.fromkeys(ids));s=state();h=s.setdefault('deleted',{});ed=s.setdefault('edits',{});lookup={p['id']:p for p in products}
 if action=='restore':
  if any(pid not in h for pid in ids):raise ValueError('所选产品已恢复，请刷新列表')
 elif any(pid not in lookup for pid in ids):raise ValueError('所选产品已变化，请刷新列表')
 if action=='category' and (not isinstance(category,str) or not category.strip() or len(category)>100):raise ValueError('请填写产品分类（100字以内）')
 if action not in ['delete','restore','category']:raise ValueError('不支持的批量操作')
 now=datetime.datetime.now().astimezone().isoformat()
 for pid in ids:
  if action=='restore':h.pop(pid,None)
  elif action=='delete':h[pid]={'name':lookup[pid]['name'],'deleted_at':now}
  elif action=='category':ed.setdefault(pid,{})['category']=category.strip()
 write(s)
def apply(v):
 s=state();h=s.get('deleted',{});ed=s.get('edits',{})
 for p in v['products']:p.update(ed.get(p['id'],{}))
 v['deleted_products']=[dict(p,deleted_at=h[p['id']]['deleted_at']) for p in v['products'] if p['id'] in h]
 v['products']=[p for p in v['products'] if p['id'] not in h]
 for r in v['recordings']:r['product_ids']=[pid for pid in r['product_ids'] if pid not in h]
 v['stats']['raw_with_products']=sum(bool(r['product_ids']) for r in v['recordings'] if r['kind']=='原始回放')
 return v
