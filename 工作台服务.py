from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse,parse_qs,unquote
import json,sys,threading,mimetypes,datetime,subprocess
from 建立索引 import BASE,DATA,ROOT,build
from 商品资源 import decorate,selection,save_resources,import_shop
from 产品筛选 import apply,change,bulk
from 产品合并 import merge
from 商品核验 import verified
APP=BASE;LOCK=threading.Lock()
def load():return json.loads((DATA/'素材索引.json').read_text())
def edits():
 p=DATA/'手动补充.json'
 return json.loads(p.read_text()) if p.exists() else {'products':[],'notes':{}}
def effective():
 v=load();e=edits();v['products']+=e.get('products',[])
 for r in v['recordings']:
  r['note']=e.get('notes',{}).get(r['id'],'')
  for p in e.get('products',[]):
   if any(a['recording_id']==r['id'] for a in p['appearances']):r['product_ids'].append(p['id'])
 return verified(apply(merge(decorate(v))))
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def reply(self,v,code=200):
  body=json.dumps(v,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',len(body));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
 def do_GET(self):
  u=urlparse(self.path)
  if u.path=='/api/index':return self.reply(effective())
  if u.path=='/api/export':return self.reply(effective())
  if u.path=='/media':
   rid=parse_qs(u.query).get('id',[''])[0];r=next((r for r in load()['recordings'] if r['id']==rid),None)
   if not r:return self.reply({'error':'未知素材'},404)
   p=Path(r['path'])
   if not p.is_relative_to(ROOT) or not p.is_file():return self.reply({'error':'素材不可访问，请检查硬盘'},404)
   size=p.stat().st_size;start=0;end=size-1
   rg=self.headers.get('Range','')
   if rg.startswith('bytes='):
    try:
     a,b=rg[6:].split('-',1);start=int(a or 0);end=min(int(b) if b else end,end)
     if start>end or start<0:raise ValueError()
    except ValueError:return self.reply({'error':'范围无效'},416)
   self.send_response(206 if rg else 200);self.send_header('Content-Type',mimetypes.guess_type(p.name)[0] or 'video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',end-start+1)
   if rg:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
   self.end_headers()
   try:
    with p.open('rb') as f:
     f.seek(start);left=end-start+1
     while left:
      chunk=f.read(min(left,1024*1024))
      if not chunk:break
      self.wfile.write(chunk);left-=len(chunk)
   except (BrokenPipeError,ConnectionResetError):pass
   return
  route='/index.html' if u.path=='/' else unquote(u.path)
  p=(APP/route.lstrip('/')).resolve()
  if not p.is_relative_to(APP) or not p.is_file():return self.reply({'error':'页面不存在'},404)
  b=p.read_bytes();self.send_response(200);self.send_header('Content-Type',(mimetypes.guess_type(str(p))[0] or 'application/octet-stream')+'; charset=utf-8');self.send_header('Content-Length',len(b));self.end_headers();self.wfile.write(b)
 def do_POST(self):
  # Same-origin local changes only; NAS is never writable through this service.
  origin=self.headers.get('Origin','')
  if origin and origin!=f'http://{self.headers.get("Host")}':return self.reply({'error':'仅允许本地工作台操作'},403)
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n>8000000:raise ValueError('提交内容过大')
   body=json.loads(self.rfile.read(n) or '{}')
   if self.path=='/api/bulk':
    with LOCK:bulk(body.get('product_ids'),effective()['products'],body.get('action'),body.get('category',''))
    return self.reply(effective())
   if self.path in ['/api/delete','/api/restore']:
    with LOCK:change(body.get('product_id'),effective()['products'],self.path=='/api/restore')
    return self.reply(effective())
   if self.path=='/api/shop-import':
    with LOCK:count=import_shop(body)
    return self.reply({'count':count})
   if self.path=='/api/resources':
    with LOCK:save_resources(body.get('product_id'),body,{p['id'] for p in effective()['products'] if p['appearances']})
    return self.reply(effective())
   if self.path=='/api/export':
    folder=DATA/'导出';folder.mkdir(exist_ok=True)
    p=folder/('猫哥素材索引_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json')
    p.write_text(json.dumps(effective(),ensure_ascii=False,indent=2))
    return self.reply({'path':str(p)})
   if self.path=='/api/refresh':
    with LOCK:build()
    return self.reply(effective())
   if self.path=='/api/save':
    with LOCK:
     e=edits();ids={r['id'] for r in load()['recordings']};rid=body.get('recording_id')
     if rid not in ids:raise ValueError('请先选择已登记的素材')
     if body.get('note') is not None:e['notes'][rid]=str(body['note'])[:4000]
     if body.get('name'):
      name=str(body['name']).strip()[:300];a=float(body.get('start') or 0);b=float(body.get('end') or 0)
      if a<0 or (b and b<=a):raise ValueError('结束秒数必须大于开始秒数')
      key=body.get('product_id') or 'U-'+datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
      q={'id':key,'name':name,'category':str(body.get('category','其他 / 待分类'))[:100],'aliases':[],'description':str(body.get('description',''))[:4000],'cautions':['用户手动补充记录'],'appearances':[{'recording_id':rid,'basis':'手动补充','windows':[[a,b]] if b else []}],'evidence':'本工作台手动补充'}
      q.update(selection(body))
      prev=next((p for p in e['products'] if p['id']==key),None)
      if prev:e['products'][e['products'].index(prev)]=q
      else:e['products'].append(q)
     p=DATA/'手动补充.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(e,ensure_ascii=False,indent=2));t.replace(p)
    return self.reply(effective())
   return self.reply({'error':'接口不存在'},404)
  except Exception as exc:self.reply({'error':str(exc)},400)
if __name__=='__main__':
 port=int(sys.argv[1]) if len(sys.argv)>1 else 8787
 if not (DATA/'素材索引.json').exists():build()
 server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
 print(f'工作台已启动：http://127.0.0.1:{port}',flush=True)
 if '--open' in sys.argv:threading.Timer(0.6,lambda:subprocess.run(['/usr/bin/open',f'http://127.0.0.1:{port}'])).start()
 try:server.serve_forever()
 except KeyboardInterrupt:server.server_close()
