// Source-derived minimal DOM logic probe. This is NOT a browser or HTML parser.
// Native validation, layout, focus, pointer/keyboard dispatch, and AT are not implemented.
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = '/workspace/scratch/1acf7c2e1e4d';
const subject = path.join(root, 'evaluation/common/subject');
const output = path.join(root, 'anything-frontend-D/evidence/D/evaluation/report-logic-log.json');
const records = [];
function sha(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function source(file) {
  const bytes = fs.readFileSync(path.join(subject, file));
  return {file, sha256:sha(bytes), code:bytes.toString('utf8').match(/<script>([\s\S]*?)<\/script>/)[1]};
}
class Element {
  constructor() { this.value=''; this.checked=false; this.disabled=false; this.textContent=''; this.children=[]; this.listeners={}; }
  addEventListener(type, fn) { this.listeners[type]=fn; }
  append(child) { this.children.push(child); }
  replaceChildren(...children) { this.children=children; }
}
function harness(file) {
  const s=source(file), elements={}, timers=[];
  const get=id => elements[id] ||= new Element();
  const document={querySelector:get,createElement:()=>new Element()};
  if (file==='registration.html') {
    get('#name'); get('#email'); get('#seats').value='1'; get('#count').textContent='0';
    get('#status').textContent='必要事項を入力してください。';
    get('#registration').reset=()=>{get('#name').value='';get('#email').value='';get('#seats').value='1';};
  } else { get('#query').value='';get('#filter').value='all'; }
  class FormData {
    constructor() { this.entries=['name','email','seats'].map(id=>[id,get('#'+id).value]); }
    [Symbol.iterator]() { return this.entries[Symbol.iterator](); }
  }
  const context=vm.createContext({document,FormData,setTimeout:(callback,delay)=>timers.push({callback,delay})});
  vm.runInContext(s.code,context,{filename:s.file});
  return {get,s,timers,context,fire:(id,type)=>get(id).listeners[type]({preventDefault(){}}),flush:async()=>{
    const delays=timers.map(t=>t.delay); while(timers.length) timers.shift().callback(); await Promise.resolve(); return delays;
  }};
}
function regSnapshot(h) {
  return {name:h.get('#name').value,email:h.get('#email').value,seats:h.get('#seats').value,count:h.get('#count').textContent,status:h.get('#status').textContent,fail:h.get('#fail').checked,queued:h.timers.length};
}
function fill(h,seats='2') {h.get('#name').value='確認 太郎';h.get('#email').value='qa@example.test';h.get('#seats').value=seats;}
function listSnapshot(h) {
  return {summary:h.get('#summary').textContent,page:h.get('#page').textContent,rows:h.get('#rows').children.map(row=>row.children.map(cell=>cell.textContent)),prevDisabled:h.get('#prev').disabled,nextDisabled:h.get('#next').disabled,query:h.get('#query').value,filter:h.get('#filter').value};
}
(async()=>{
  let h=harness('registration.html'); fill(h);
  let pending=h.fire('#registration','submit');const start=regSnapshot(h);const delay=await h.flush();await pending;
  assert.equal(h.get('#count').textContent,'1');
  records.push({id:'REG-NORMAL',engine:'minimal DOM logic harness',before_completion:start,timer_delay_requested_ms:delay,after:regSnapshot(h)});
  h=harness('registration.html');fill(h);h.get('#fail').checked=true;
  pending=h.fire('#registration','submit');await h.flush();await pending;
  const failed=regSnapshot(h);assert.equal(failed.name,'');assert.equal(failed.email,'');assert.equal(failed.seats,'1');assert.equal(failed.count,'0');
  fill(h);pending=h.fire('#registration','submit');await h.flush();await pending;
  records.push({id:'REG-ERROR-REENTRY',engine:'minimal DOM logic harness',after_failure:failed,recovery_action:'manually re-enter the original three input values; invoke submit handler again',after_reentry_retry:regSnapshot(h)});
  h=harness('registration.html');fill(h);
  const p1=h.fire('#registration','submit'),p2=h.fire('#registration','submit');const doublePending=regSnapshot(h);
  await h.flush();await Promise.all([p1,p2]);assert.equal(h.get('#count').textContent,'2');
  records.push({id:'REG-REPEAT',engine:'minimal DOM logic harness',method:'Invoke captured submit listener twice before draining its scheduled callbacks. No click/keyboard event was simulated.',pending:doublePending,after:regSnapshot(h)});
  for(const seats of ['1','8']) {
    h=harness('registration.html');fill(h,seats);pending=h.fire('#registration','submit');await h.flush();await pending;
    assert.equal(h.get('#count').textContent,'1');
    records.push({id:'REG-VALID-'+seats,engine:'minimal DOM logic harness',native_validation:'not implemented; handler receives a known valid payload',after:regSnapshot(h)});
  }
  h=harness('requests.html');const trace=[{action:'initial source evaluation',...listSnapshot(h)}];
  h.fire('#next','click');trace.push({action:'invoke next handler',...listSnapshot(h)});
  h.fire('#next','click');trace.push({action:'invoke next handler',...listSnapshot(h)});
  assert.deepEqual(trace.map(t=>t.rows.map(r=>r[0])),[['R-101','R-102','R-103'],['R-104','R-105','R-106'],['R-107','R-108']]);
  records.push({id:'LIST-NORMAL',engine:'minimal DOM logic harness',trace});
  h.get('#filter').value='待ち';h.fire('#filter','change');const stale=listSnapshot(h);
  assert.equal(stale.summary,'2件の依頼');assert.equal(stale.page,'3 / 1');assert.equal(stale.rows.length,0);
  h.fire('#prev','click');const once=listSnapshot(h);h.fire('#prev','click');const twice=listSnapshot(h);
  assert.deepEqual(twice.rows.map(r=>r[0]),['R-101','R-104']);
  records.push({id:'LIST-FILTER-AFTER-PAGE',engine:'minimal DOM logic harness',after_filter:stale,after_prev_once:once,after_prev_twice:twice});
  h.fire('#clear','click');h.get('#query').value='存在しない依頼';h.fire('#query','input');const empty=listSnapshot(h);
  assert.equal(empty.summary,'0件の依頼');assert.equal(empty.rows.length,0);
  h.fire('#clear','click');const cleared=listSnapshot(h);assert.equal(cleared.summary,'8件の依頼');
  records.push({id:'LIST-EMPTY-CLEAR',engine:'minimal DOM logic harness',empty,after_clear:cleared});
  h.fire('#next','click');h.get('#query').value='湯のみ';h.fire('#query','input');const search=listSnapshot(h);
  assert.equal(search.summary,'1件の依頼');assert.equal(search.page,'2 / 1');assert.equal(search.rows.length,0);
  h.fire('#clear','click');records.push({id:'LIST-SEARCH-AFTER-PAGE',engine:'minimal DOM logic harness',after_query:search,after_clear:listSnapshot(h)});
  const log={schema:'assigned condition-source-logic-log/v1',created_at:new Date().toISOString(),node:process.version,os:process.platform,
    engine:'minimal DOM logic harness; inline JavaScript extracted without modification',
    limitations:['No browser was started.','No CSS or real DOM layout.','No native form validity; invalid-input submission is deliberately not tested.','No focus, actual click, keyboard, screenshot, accessibility tree, or assistive-technology observation.','Timers are manually drained; requested delay is recorded but wall-clock latency is not measured.','FormData and reset are stubs for the three specified inputs; the form reset consequence is additionally supported by source and HTML Standard.'],
    artifacts:['registration.html','requests.html'].map(file=>{const s=source(file);return {path:'evaluation/common/subject/'+file,sha256:s.sha256};}),
    records};
  fs.writeFileSync(output,JSON.stringify(log,null,2)+'\n');
  process.stdout.write(JSON.stringify({output,records:records.length,assertions:'all diagnostic expectations observed',engine:log.engine})+'\n');
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1;});
