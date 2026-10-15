function linkOptions(rows,selected=''){return '<option value="">不更改链接 / 暂不绑定</option>'+rows.map(r=>'<option value="'+esc(r.url)+'" '+(selected===r.url?'selected':'')+'>'+esc(r.name)+' · '+esc((new URL(r.url)).searchParams.get('id')||(new URL(r.url)).searchParams.get('promotion_id')||'')+'</option>').join('')}
function relevantLinks(name){let n=name.toLowerCase().replace(/\s/g,''),keys=n.split(/[\s、,]+/).filter(k=>k.length>=2);let found=keys.filter(k=>n.includes(k));return (data.shop_links||[]).filter(r=>{let a=r.name.toLowerCase().replace(/\s/g,'');return n&&((a.length>=5&&n.includes(a))||found.some(k=>a.includes(k)))})}
async function imageData(input){let f=input.files[0];if(!f)return '';if(f.size>5*1024*1024)throw Error('图片不能超过5MB');if(!['image/png','image/jpeg','image/webp'].includes(f.type))throw Error('请选择PNG、JPG或WebP图片');return new Promise((resolve,reject)=>{let r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=reject;r.readAsDataURL(f)})}
function linkBlock(p){let rows=p.candidate_links||[],bound=p.product_url?'<div class="appearance"><b>已选择：'+esc(p.link_name||p.name)+'</b><div class="path">'+esc(p.product_url)+'</div><div class="buttons"><a class="btn" href="'+esc(p.product_url)+'" target="_blank" rel="noopener">打开商品链接 ↗</a><button class="btn" data-copy="'+esc(p.product_url)+'">复制链接</button></div><p class="subtle">'+esc(p.link_status||'请核对规格、库存与当前商品页')+'</p></div>':'';return '<section class="productlinks"><h3>商品图片与链接</h3><button class="btn" data-resource="'+esc(p.id)+'">设置图片 / 选择商品链接</button>'+bound+(rows.length?'<p class="subtle">从原商品库找到以下关联候选，点击选择具体款式；仅列出有素材的本商品相关链接。</p>'+rows.map(r=>'<div class="appearance"><b>'+esc(r.name)+'</b><p class="subtle">'+esc(r.match_status||'原工作台名称线索，核对具体款式')+' · 链接有效性未验证</p><div class="buttons"><button class="btn" data-select-link="'+esc(p.id)+'" data-url="'+esc(r.url)+'">选择此链接</button><a class="btn" target="_blank" rel="noopener" href="'+esc(r.url)+'">打开商品 ↗</a><button class="btn" data-copy="'+esc(r.url)+'">复制链接</button></div></div>').join(''):(p.product_url?'':'<div class="notice">尚未取得明确对应链接。仅补充有素材的商品，不按相似外观猜测款式。</div>'))+'</section>'}
var oldRender=render;render=function(){oldRender();if(view==='products'){document.querySelectorAll('#results .card').forEach((el,i)=>{let p=items[(page-1)*24+i];let box=document.createElement('div');box.className='productphoto';box.innerHTML=p.image?'<img loading="lazy" src="'+esc(p.image)+'" alt="'+esc(p.name)+'的商品链接图片">':'<span>待补商品链接图</span>';el.prepend(box);if(p.product_url||p.candidate_links?.length){let tag=document.createElement('span');tag.className='subtle';tag.textContent=p.product_url?'已绑定商品链接':'有相关链接可选';el.append(tag)}})}};
var oldShowProduct=showProduct;showProduct=function(id){oldShowProduct(id);let p=productMap[id];$('#dbody').insertAdjacentHTML('afterbegin',(p.image?'<figure class="detailphoto"><img src="'+esc(p.image)+'" alt="'+esc(p.name)+'"><figcaption class="subtle">'+esc(p.image_source||'产品实物图片')+'</figcaption></figure>':'')+linkBlock(p))};
$('#editor .formgrid').insertAdjacentHTML('beforeend','<label class="wide">补充商品链接中的图片（PNG / JPG / WebP，5MB以内）<input id="fimage" type="file" accept="image/png,image/jpeg,image/webp"><img id="fimagepreview" style="display:none;max-height:150px;object-fit:contain"></label><label class="wide">对应商品链接（来自原商品工作台）<select id="fshop"><option value="">先填写产品名称，再选对应款式</option></select><span class="subtle">同品牌不同型号需分别核对，不会自动绑定。</span></label>');
$('#fname').addEventListener('input',()=>{$('#fshop').innerHTML=linkOptions(relevantLinks($('#fname').value))});$('#fimage').onchange=()=>{let f=$('#fimage').files[0];$('#fimagepreview').style.display=f?'block':'none';if(f)$('#fimagepreview').src=URL.createObjectURL(f)};
var oldEdit=edit;edit=function(rid){oldEdit(rid);$('#fshop').innerHTML=linkOptions([]);$('#fimagepreview').style.display='none'};
document.body.insertAdjacentHTML('beforeend','<dialog id="resources"><div class="dhead"><div><div class="eyebrow">已有素材商品 · 图片与链接</div><h2 id="resourceTitle"></h2></div><button class="btn close">关闭</button></div><form id="resourceForm" class="dbody"><input type="hidden" id="resourceId"><div class="formgrid"><label class="wide">补充商品链接中的图片<input id="resourceImage" type="file" accept="image/png,image/jpeg,image/webp"><img id="resourcePreview" style="max-height:240px;object-fit:contain"></label><label class="wide">选择对应商品链接<select id="resourceLink"></select></label></div><div class="notice">原商品工作台仅读取。链接按具体型号、颜色和配置核对后选择；保存到本任务目录。</div><button class="btn primary" style="margin-top:20px">保存图片和链接</button></form></dialog><dialog id="shopimport"><div class="dhead"><h2>只读链接资料导入</h2><button class="btn close">关闭</button></div><form class="dbody" id="shopImportForm"><p class="subtle">仅作为已有素材商品的链接候选。不会新增无素材商品，也不修改原工作台。</p><textarea id="shopImportText" aria-label="商品库只读资料" style="width:100%;height:240px"></textarea><button class="btn primary">导入链接资料</button></form></dialog>');
let imp=document.createElement('button');imp.className='btn';imp.id='shopImportButton';imp.textContent='补充链接资料';$('#export').parentNode.append(imp);imp.onclick=()=>$('#shopimport').showModal();
function resourceEdit(id,url,mode='library'){
 let p=productMap[id];$('#resourceForm').reset();$('#resourceId').value=id;$('#resourceTitle').textContent=productPreviewName(p);
 $('#resourcePreview').src=p.image||'';$('#resourcePreview').style.display=p.image?'block':'none';
 let rows=[...(p.candidate_links||[])];if(p.product_url&&!rows.some(r=>r.url===p.product_url))rows.unshift({url:p.product_url,name:p.link_name||p.name});
 if(url&&!rows.some(r=>r.url===url)){let r=(data.shop_links||[]).find(r=>r.url===url);if(r)rows.unshift(r)}
 $('#resourceLink').innerHTML=linkOptions(rows,url||p.product_url||'');
 $('#manualLinkName').value=productPreviewName(p);$('#manualLinkUrl').value=p.link_source==='用户手动添加'?(p.product_url||''):'';
 $('#resourceMode').value=mode;resourceModeChanged();$('#resources').showModal();
}
$('#resourceImage').onchange=()=>{let f=$('#resourceImage').files[0];$('#resourcePreview').style.display=f?'block':'none';if(f)$('#resourcePreview').src=URL.createObjectURL(f)};
document.addEventListener('click',e=>{let b=e.target.closest('button');if(!b)return;if(b.dataset.resource)resourceEdit(b.dataset.resource);if(b.dataset.selectLink)resourceEdit(b.dataset.selectLink,b.dataset.url)});
$('#resourceForm').onsubmit=async e=>{
 e.preventDefault();if(!online)return toast('请先启动本地工作台');let button=$('#resourceForm button[type="submit"]');button.disabled=true;
 try{let pid=$('#resourceId').value,mode=$('#resourceMode').value;
  data=await request('/api/resources',{product_id:pid,image_data:await imageData($('#resourceImage')),link_mode:mode,shop_url:mode==='library'?$('#resourceLink').value:'',manual_url:mode==='manual'?$('#manualLinkUrl').value:'',manual_name:$('#manualLinkName').value});
  initialize();$('#resources').close();showProduct(pid);toast('商品图片和链接已保存');
 }catch(e){toast(e.message)}finally{button.disabled=false}
};
$('#shopImportForm').onsubmit=async e=>{e.preventDefault();try{let result=await request('/api/shop-import',{products:JSON.parse($('#shopImportText').value)});data=await(await fetch('/api/index')).json();initialize();$('#shopimport').close();toast('已读取 '+result.count+' 条相关链接资料')}catch(e){toast(e.message)}};
render();

// Manual binding is local to this product; the external product library stays read-only.
$('#resourceLink').closest('label').id='libraryLinkFields';
$('#libraryLinkFields').insertAdjacentHTML('beforebegin','<label class="wide">链接添加方式<select id="resourceMode"><option value="library">从已有商品库选择 / 保留当前链接</option><option value="manual">手动添加商品链接</option></select></label>');
$('#libraryLinkFields').insertAdjacentHTML('afterend','<div class="wide" id="manualLinkFields" hidden><label style="display:flex;flex-direction:column;gap:7px;margin-bottom:14px">链接名称<input id="manualLinkName" maxlength="400" placeholder="例如：视频同款"></label><label style="display:flex;flex-direction:column;gap:7px">商品链接<input id="manualLinkUrl" type="url" maxlength="3000" placeholder="粘贴完整的 https:// 商品链接"><span class="subtle">保存后替换此商品当前绑定的链接；手动链接会标注尚未核验。</span></label></div>');
$('#resourceForm').querySelector('button.primary').type='submit';
function resourceModeChanged(){let manual=$('#resourceMode').value==='manual';$('#manualLinkFields').hidden=!manual;$('#libraryLinkFields').hidden=manual;$('#libraryLinkFields').style.display=manual?'none':'flex';$('#manualLinkUrl').required=manual;$('#resourceLink').disabled=manual;$('#manualLinkUrl').disabled=!manual;$('#manualLinkName').disabled=!manual;}
$('#resourceMode').onchange=resourceModeChanged;resourceModeChanged();
var manualLinkBlockBase=linkBlock;linkBlock=function(p){return manualLinkBlockBase(p)+'<div class="buttons" style="margin:12px 0 20px"><button class="btn" data-manual-link="'+esc(p.id)+'">手动添加链接</button>'+(p.product_url?'<button class="btn danger" data-delete-link="'+esc(p.id)+'">删除此商品链接</button>':'')+'</div>'};
document.addEventListener('click',async e=>{
 let b=e.target.closest('button');if(!b)return;
 if(b.dataset.manualLink)return resourceEdit(b.dataset.manualLink,undefined,'manual');
 if(b.dataset.deleteLink){
  if(!online)return toast('请先启动本地工作台');let pid=b.dataset.deleteLink;
  if(!confirm('删除此商品当前绑定的链接？商品和素材会保留。'))return;
  b.disabled=true;try{data=await request('/api/resources',{product_id:pid,action:'delete_link'});initialize();showProduct(pid);toast('已删除此商品的链接绑定')}catch(e){toast(e.message);b.disabled=false}
 }
});
