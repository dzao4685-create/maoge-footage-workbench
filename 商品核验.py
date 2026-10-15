from pathlib import Path
import json
DATA=Path(__file__).resolve().parent/'数据'
def verified(v):
 try:a=json.loads((DATA/'商品核验.json').read_text())
 except (OSError,ValueError):return v
 for p in v['products']+v.get('deleted_products',[]):
  z=a.get('products',{}).get(p['id'])
  if z:p['verification']=z;p['candidate_links']=[r for r in z.get('candidates',[]) if r.get('url')!=p.get('product_url')]
 v['verification_summary']=dict(a.get('summary',{}))
 v['verification_summary']['bound_products']=sum(bool(p.get('product_url')) for p in v['products'])
 v['verification_summary']['remaining_products']=len(v['products'])-v['verification_summary']['bound_products']
 return v
