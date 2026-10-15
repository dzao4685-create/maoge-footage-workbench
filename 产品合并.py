from pathlib import Path
from copy import deepcopy
import json
FILE=Path(__file__).resolve().parent/'数据'/'产品合并.json'
def unique(items):
 out=[]
 for x in items:
  if x not in out:out.append(x)
 return out
def merge(v):
 if not FILE.exists():return v
 groups=json.loads(FILE.read_text()).get('groups',[]);lookup={p['id']:p for p in v['products']};mapping={};applied=[]
 for g in groups:
  root=lookup.get(g['canonical_id'])
  if not root:continue
  members=[root]+[lookup[i] for i in g['merged_ids'] if i in lookup]
  if len(members)<2:continue
  urls=unique([p['product_url'] for p in members if p.get('product_url')])
  if len(urls)>1 and not root.get('link_override'):continue
  root['merged_from']=[deepcopy(p) for p in members]
  root['merged_product_ids']=[p['id'] for p in members[1:]]
  root['merge_notes']=g['reason']
  root['aliases']=unique(root.get('aliases',[])+[n for p in members[1:] for n in [p['name']]+p.get('aliases',[])])
  root['cautions']=unique([n for p in members for n in p.get('cautions',[])])
  root['evidence_paths']=unique([n for p in members for n in p.get('evidence_paths',[p.get('evidence','')]) if n])
  root['source_descriptions']=[{'id':p['id'],'name':p['name'],'description':p.get('description',''),'recording_ids':[a['recording_id'] for a in p['appearances']]} for p in root['merged_from']]
  appearances={}
  for p in root['merged_from']:
   for a in p.get('appearances',[]):
    rid=a['recording_id'];dest=appearances.setdefault(rid,{'recording_id':rid,'basis':a.get('basis',''),'windows':[],'source_records':[]})
    dest['source_records'].append({'product_id':p['id'],**deepcopy(a)})
    dest['basis']='；'.join(unique([dest['basis']]+[a.get('basis','')]))
    dest['windows']=unique(dest['windows']+a.get('windows',[]))
  for a in appearances.values():a['windows'].sort(key=lambda w:w[0])
  root['appearances']=list(appearances.values())
  for field in ['product_url','link_name','link_source','link_status','image','image_source','footage_image']:
   if root.get('link_override') and field in ['product_url','link_name','link_source','link_status']:continue
   if not root.get(field):
    value=next((p.get(field) for p in members[1:] if p.get(field)),None)
    if value:root[field]=value
  root['candidate_links']=unique([x for p in members for x in p.get('candidate_links',[])])
  for p in members[1:]:mapping[p['id']]=root['id']
  applied.append({'canonical_id':root['id'],'merged_ids':root['merged_product_ids'],'reason':g['reason']})
 v['products']=[p for p in v['products'] if p['id'] not in mapping]
 for r in v['recordings']:r['product_ids']=unique([mapping.get(i,i) for i in r['product_ids']])
 v['product_merges']=applied
 return v
