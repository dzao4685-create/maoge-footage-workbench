from pathlib import Path
import json,re,base64,hashlib,datetime
from urllib.parse import urlsplit
BASE=Path(__file__).resolve().parent;DATA=BASE/'数据';APP=BASE
def read(p,default):
 try:return json.loads(p.read_text())
 except (OSError,ValueError):return default
def clean(s):return re.sub(r'[^a-z0-9\u4e00-\u9fff]','',s.lower())
def shop():return read(DATA/'商品库只读快照.json',{}).get('products',[])
def related(p,rows):
 names=[p.get('name','')]+p.get('aliases',[]);text=clean(' '.join(names));keys=[clean(a) for a in names if len(clean(a))>=2];found=[k for k in keys if k in text];out=[]
 for r in rows:
  n=clean(r['name']);exact=any(clean(a)==n for a in names)
  if p.get('id','!') in r.get('image','') or exact or (len(n)>=5 and n in text) or any(k in n for k in found):out.append(dict(r,match_status='名称一致，仍需核对款式' if exact else '同品牌/名称线索，待核对款式'))
 return out
def decorate(v):
 rows=shop();rs=read(DATA/'商品图片链接补充.json',{})
 for p in v['products']:
  oldimage=p.pop('image',None)
  uploaded=oldimage if p.get('image_source')=='用户上传产品图片' and p.get('product_url') else None
  if oldimage:p['footage_image']=oldimage
  p.update(rs.get(p['id'],{}));p['candidate_links']=related(p,rows)
  selected=next((r for r in rows if r['url']==p.get('product_url')),None)
  uploaded=rs.get(p['id'],{}).get('image',uploaded)
  p.pop('image',None);p['image_source']='待添加对应商品链接图'
  if uploaded and p.get('product_url'):p['image']=uploaded;p['image_source']='用户补充商品链接图'
  if selected and selected.get('image') and '/PF-' not in selected['image']:p['image']=selected['image'];p['image_source']='商品链接原图'
 v['shop_links']=rows;return v
def selection(body):
 result={};data=body.get('image_data')
 if body.get('action')=='delete_link':
  return {'product_url':'','link_name':'','link_source':'','link_status':'已手动删除商品链接绑定','link_override':True}
 manual=body.get('manual_url')
 if body.get('link_mode')=='manual':
  if not isinstance(manual,str) or not manual.strip():raise ValueError('请输入商品链接')
  manual=manual.strip()
  try:parsed=urlsplit(manual)
  except ValueError:raise ValueError('商品链接格式无效')
  if len(manual)>3000 or re.search(r'\s',manual) or parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
   raise ValueError('请填写完整的 http 或 https 商品链接，不支持带账号密码的链接')
  name=body.get('manual_name','手动添加的商品链接')
  if not isinstance(name,str):raise ValueError('链接名称格式无效')
  result.update(link_override=True,product_url=manual,link_name=name.strip()[:400] or '手动添加的商品链接',link_source='用户手动添加',link_status='用户手动添加；尚未核验可用性与同款规格')
 if data:
  m=re.fullmatch(r'data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=\r\n]+)',data)
  if not m:raise ValueError('图片支持PNG、JPG、WebP')
  raw=base64.b64decode(m[2],validate=True)
  if len(raw)>5*1024*1024:raise ValueError('图片不能超过5MB')
  if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff') or (raw[:4]==b'RIFF' and raw[8:12]==b'WEBP')):raise ValueError('无效图片')
  name='upload-'+hashlib.sha256(raw).hexdigest()[:24]+'.'+{'png':'png','jpeg':'jpg','webp':'webp'}[m[1]];folder=APP/'product-images';folder.mkdir(exist_ok=True);(folder/name).write_bytes(raw);result.update(image='product-images/'+name,image_source='用户上传产品图片')
 url=body.get('shop_url')
 if url and body.get('link_mode')!='manual':
  r=next((r for r in shop() if r.get('url')==url),None)
  if not r:raise ValueError('请选择从原商品库导入的链接')
  result.update(link_override=True,product_url=url,link_name=r['name'],link_source='用户导入的只读商品资料',link_status='用户选择；使用前核对款式与库存')
 return result
def save_resources(pid,body,ids):
 if pid not in ids:raise ValueError('只能为已有素材的商品补充')
 rs=read(DATA/'商品图片链接补充.json',{});payload=dict(body)
 current=rs.get(pid,{}).get('product_url')
 if payload.get('link_mode')!='manual' and current and payload.get('shop_url')==current and not any(r.get('url')==current for r in shop()):payload['shop_url']=''
 change=selection(payload)
 history=read(DATA/'商品链接修改记录.json',{'changes':[]})
 history.setdefault('changes',[]).append({'product_id':pid,'changed_at':datetime.datetime.now().astimezone().isoformat(),'action':body.get('action') or body.get('link_mode') or 'resources','before':dict(rs.get(pid,{})),'update':change})
 (DATA/'商品链接修改记录.json').write_text(json.dumps(history,ensure_ascii=False,indent=2))
 rs.setdefault(pid,{}).update(change);(DATA/'商品图片链接补充.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2))
def import_shop(body):
 rows=[]
 for x in body.get('products',[]):
  url=x.get('url','')
  if not isinstance(url,str) or not re.match(r'^https://(haohuo|alliance)\.jinritemai\.com/',url):continue
  img=x.get('image','') or ''
  if img.startswith('/'):img='' # Relative remote images require an explicit trusted source URL
  rows.append({'name':str(x.get('name',''))[:400],'url':url,'image':img,'source_status':'原商品库显示链接待核验'})
 dedup={r['name']+'|'+r['url']:r for r in rows};(DATA/'商品库只读快照.json').write_text(json.dumps({'source':'用户导入的只读商品资料','captured_at':datetime.datetime.now().astimezone().isoformat(),'products':list(dedup.values()),'usage':'只为已有素材商品提供链接候选，不新增无素材商品'},ensure_ascii=False,indent=2));return len(dedup)
