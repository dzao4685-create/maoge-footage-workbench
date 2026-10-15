from 工作台服务 import effective
import sys,json
v=effective();words=' '.join(sys.argv[1:]).lower().split();rs={r['id']:r for r in v['recordings']}
for p in v['products']:
 for a in p['appearances']:
  r=rs[a['recording_id']];hay=' '.join([p['name'],p['category'],*p['aliases'],r['name'],r['date']]).lower()
  if all(w in hay for w in words):print(json.dumps({'产品':p['name'],'分类':p['category'],'素材':r['name'],'日期':r['date'],'路径':r['path'],'回查秒数':a['windows'],'依据':a['basis'],'产品图片':p.get('image'),'商品链接':p.get('product_url'),'候选商品链接':p.get('candidate_links',[])},ensure_ascii=False))
