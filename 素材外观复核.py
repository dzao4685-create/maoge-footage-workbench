from pathlib import Path
import json
from copy import deepcopy

def apply_visual_reviews(v):
    path=Path(__file__).resolve().parent/'数据'/'素材外观复核.json'
    if not path.exists(): return v
    patch=json.loads(path.read_text())
    products={p['id']:p for p in v['products']}
    recordings={r['id']:r for r in v['recordings']}
    for pid,z in patch.get('products',{}).items():
        p=products.get(pid)
        if not p: continue
        p['description']=z.get('description',p.get('description',''))
        for field in ['aliases','cautions']:
            p[field]=list(dict.fromkeys(p.get(field,[])+z.get(field,[])))
        apps={a['recording_id']:a for a in p.get('appearances',[])}
        for a in z.get('appearances',[]):
            rid=a['recording_id']
            if rid not in recordings: continue
            apps[rid]=deepcopy(a)
            r=recordings[rid]
            if pid not in r['product_ids']:r['product_ids'].append(pid)
            r['status']='已有外观复核记录'
            item={'name':p['name'],'category':p['category'],'windows':a['windows'],'description':a.get('visual_identity',''),'evidence':a.get('evidence',''),'timing_basis':a.get('timing_basis','回查窗口')}
            r['analysis']=[x for x in r.get('analysis',[]) if x.get('name')!=p['name']]+[item]
        p['appearances']=sorted(apps.values(),key=lambda a:recordings[a['recording_id']]['date'])
        p['visual_candidates']=deepcopy(z.get('visual_candidates',[]))
        p['visual_reviewed_at']=patch.get('checked_at')
    v['visual_reviews_updated_at']=patch.get('checked_at')
    return v
