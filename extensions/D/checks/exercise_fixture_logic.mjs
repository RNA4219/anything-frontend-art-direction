#!/usr/bin/env node
/** Execute the fixtures' actual scripts in a minimal, non-rendering DOM model.
 * This is a unit-level probe, not a browser, accessibility, native validation,
 * timing, hit-testing, layout, focus, or human-usability test.
 */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';

const skillDir=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const fixtureDir=path.join(skillDir,'tests','fixtures');
const observations=[];
class Element {
  constructor(value=''){this.value=value;this.checked=false;this.disabled=false;this.textContent='';this.children=[];this.listeners={};}
  addEventListener(type,fn){this.listeners[type]=fn;}
  append(child){this.children.push(child);}
  replaceChildren(...children){this.children=children;}
  async dispatch(type){return this.listeners[type]?.({preventDefault(){}});}
}
function load(name){
  const raw=fs.readFileSync(path.join(fixtureDir,name),'utf8');
  const script=raw.match(/<script>([\s\S]*?)<\/script>/i)[1];
  const elements={};
  for(const id of raw.matchAll(/\bid="([^"]+)"/g))elements['#'+id[1]]=new Element();
  if(name==='registration.html'){
    elements['#seats'].value='1';
    elements['#registration'].reset=()=>{elements['#name'].value='';elements['#email'].value='';elements['#seats'].value='1';};
  }else elements['#filter'].value='all';
  const document={querySelector(selector){if(!elements[selector])throw Error('unmodeled selector '+selector);return elements[selector];},createElement(){return new Element();}};
  class FormDataMock {constructor(){this.items=['name','email','seats'].map(k=>[k,elements['#'+k].value]);}[Symbol.iterator](){return this.items[Symbol.iterator]();}}
  vm.runInNewContext(script,{document,FormData:FormDataMock,setTimeout:fn=>{queueMicrotask(fn);},console},{filename:name,timeout:1000});
  return {raw,e:elements,sha256:crypto.createHash('sha256').update(raw).digest('hex')};
}
function fill(e){e['#name'].value='確認 太郎';e['#email'].value='qa@example.test';e['#seats'].value='2';}
function formState(e){return {name:e['#name'].value,email:e['#email'].value,seats:e['#seats'].value,count:e['#count'].textContent,status:e['#status'].textContent};}
function listState(e){return {summary:e['#summary'].textContent,page:e['#page'].textContent,rows:e['#rows'].children.map(r=>r.children.map(c=>c.textContent)),previousDisabled:e['#prev'].disabled,nextDisabled:e['#next'].disabled};}
function record(id,scenario,steps,state,assertion){observations.push({id,scenario,execution_surface:'minimal_dom_model',steps,state,probe_assertion:assertion});}

{
 const {e}=load('registration.html');fill(e);await e['#registration'].dispatch('submit');
 assert.equal(e['#count'].textContent,'1');assert.match(e['#status'].textContent,/C-001/);
 record('registration-normal','normal',['fill valid fields','submit'],formState(e),'one submission produces one mock receipt');
}
{
 const {e}=load('registration.html');fill(e);e['#fail'].checked=true;await e['#registration'].dispatch('submit');
 assert.equal(e['#name'].value,'');assert.equal(e['#email'].value,'');assert.match(e['#status'].textContent,/失敗/);
 record('registration-error','error',['fill valid fields','select failure','submit'],formState(e),'probe detects loss of form values after rejected mock request');
 fill(e);await e['#registration'].dispatch('submit');assert.equal(e['#count'].textContent,'1');
 record('registration-recovery','error',['refill cleared name/email/seats','submit'],formState(e),'recovery succeeds only after re-entry in this model');
}
{
 const {e}=load('registration.html');fill(e);await Promise.all([e['#registration'].dispatch('submit'),e['#registration'].dispatch('submit')]);
 assert.equal(e['#count'].textContent,'2');
 record('registration-repeat','boundary',['fill valid fields','dispatch submit twice before resolution'],formState(e),'probe detects duplicate accepted mock submissions');
}
{
 const {raw}=load('registration.html');assert.match(raw,/<input[^>]*id="seats"[^>]*min="1"[^>]*max="8"[^>]*required/);
 record('registration-bounds','boundary',['inspect declared input attributes'],{minimum:1,maximum:8,required:true},'source contains constraints; native enforcement remains NOT RUN');
}
{
 const {e}=load('requests.html');assert.equal(e['#rows'].children.length,3);await e['#next'].dispatch('click');assert.equal(e['#rows'].children[0].children[0].textContent,'R-104');
 record('requests-normal','normal',['initial render','next page'],listState(e),'second page has three expected fixed-data records');
 e['#filter'].value='待ち';await e['#filter'].dispatch('change');assert.equal(e['#rows'].children.length,0);assert.equal(e['#summary'].textContent,'2件の依頼');
 record('requests-filter-after-page','boundary',['on second page','filter pending'],listState(e),'probe detects count=2 but no visible rows and page=2/1');
 await e['#clear'].dispatch('click');assert.equal(e['#rows'].children.length,3);assert.equal(e['#page'].textContent,'1 / 3');
 record('requests-clear','error',['clear conditions'],listState(e),'clear restores a valid first-page state');
}
{
 const {e}=load('requests.html');e['#filter'].value='待ち';await e['#filter'].dispatch('change');assert.equal(e['#rows'].children.length,2);
 record('requests-first-page-filter','normal',['on first page','filter pending'],listState(e),'pending filter works on first page: important counterexample');
}
{
 const {e}=load('requests.html');e['#query'].value='存在しない依頼';await e['#query'].dispatch('input');assert.equal(e['#rows'].children.length,0);assert.equal(e['#summary'].textContent,'0件の依頼');assert.equal(e['#page'].textContent,'1 / 1');
 record('requests-zero','error',['search an absent name'],listState(e),'zero results are explicitly counted; clear remains available, no invented universal empty-state defect');
}
const output={schema:'design-qa-logic-probes/v1',fixture_hashes:Object.fromEntries(['registration.html','requests.html'].map(n=>[n,load(n).sha256])),probe_count:observations.length,probe_result:'PASS',product_acceptance:'NOT_ASSERTED',environment:{node:process.version,engine:'Node vm + minimal DOM doubles',timers:'microtask substitution; not real timing'},limitations:['No real browser layout, CSS, native form validation, focus, event targeting or accessibility tree.','Probe PASS means expected control/defect is observed; it does not mean the fixture is defect free.','Fixture-specific probes do not establish general Skill effectiveness.'],observations};
if(process.argv[2]){fs.mkdirSync(path.dirname(path.resolve(process.argv[2])),{recursive:true});fs.writeFileSync(process.argv[2],JSON.stringify(output,null,2)+'\n');}
process.stdout.write(JSON.stringify(output,null,2)+'\n');
