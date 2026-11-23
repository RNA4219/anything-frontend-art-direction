/**
 * Shared, author-controlled behavioral tests. Not an independent oracle/holdout.
 * Written from shared/tasks.md before the generated outputs were inspected.
 * Run: node evidence/B/experiments/evaluate.mjs [output-directory]
 */
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';
import { createReservationHarness, createImportHarness, INVENTORY_ITEMS, PHASES } from './shared/api.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const output = path.resolve(process.argv[2] || path.join(here, 'results'));
const draft = { name: '山田 太郎', people: 2 };
const clone = value => structuredClone(value);
const tick = async () => { await Promise.resolve(); await Promise.resolve(); };
const cases = [];
const add = (id, task, category, requirement, title, run) => cases.push({ id, task, category, requirement, title, run });
const R = (id, cat, req, title, fn) => add(id, 'reservation', cat, req, title, fn);
const I = (id, cat, req, title, fn) => add(id, 'import', cat, req, title, fn);

function validShape(snapshot, task) {
  assert.ok(PHASES.includes(snapshot.phase), 'phase is in the common contract');
  assert.ok(snapshot.error === null || (typeof snapshot.error.code === 'string' && typeof snapshot.error.message === 'string'));
  assert.ok(snapshot.requestKey === null || typeof snapshot.requestKey === 'string');
  const flags = task === 'reservation'
    ? ['canSubmit', 'canRetry', 'canReconcile', 'canCancel']
    : ['canStart', 'canPoll', 'canRetryFailed', 'canCancel'];
  for (const flag of flags) assert.equal(typeof snapshot[flag], 'boolean', flag);
}

async function beginImport({ c }) { c.setItems(clone(INVENTORY_ITEMS)); await c.start(); }
async function makePartial(ctx) {
  await beginImport(ctx);
  const id = ctx.c.snapshot().job.id;
  ctx.h.control.completeItem(id, 'a', 'succeeded');
  ctx.h.control.completeItem(id, 'b', 'failed');
  ctx.h.control.completeItem(id, 'c', 'succeeded');
  await ctx.c.poll();
  return id;
}
function releaseAll(h, method) { for (const request of h.control.pending(method)) h.control.release(request.id); }

R('R01', 'normal', 'initial snapshot', '初期値と操作可能性', async ({ c }) => {
  const s = c.snapshot(); validShape(s, 'reservation');
  assert.equal(s.phase, 'idle'); assert.deepEqual(s.draft, { name: '', people: '' });
  assert.equal(s.receipt, null); assert.equal(s.error, null); assert.equal(s.requestKey, null);
  assert.equal(s.canSubmit, false); assert.equal(s.canRetry, false); assert.equal(s.canReconcile, false);
});
R('R02', 'normal', 'reservation 1,4', 'server receiptによる予約完了', async ({ c, h, note }) => {
  c.setDraft(draft); assert.equal(c.snapshot().canSubmit, true);
  await c.submit(); note('submitted');
  const s = c.snapshot(); validShape(s, 'reservation');
  assert.equal(s.phase, 'succeeded'); assert.equal(s.receipt.status, 'confirmed');
  assert.equal(s.receipt.name, draft.name); assert.equal(s.receipt.people, 2);
  assert.equal(s.receipt.key, s.requestKey); assert.equal(h.control.inspect().created, 1);
});
R('R03', 'boundary', 'reservation 1,7', '人数下限1・上限8と文字列入力', async ({ factory }) => {
  for (const people of [1, 8, '2']) {
    const h = createReservationHarness(), c = factory(h.api);
    c.setDraft({ ...draft, people }); await c.submit();
    assert.equal(c.snapshot().phase, 'succeeded');
    assert.equal(c.snapshot().receipt.people, Number(people)); assert.equal(h.control.inspect().created, 1);
  }
});
R('R04', 'boundary', 'reservation 1,7', '範囲外・小数・空白を送信前に拒否', async ({ factory }) => {
  for (const invalid of [{ ...draft, people: 0 }, { ...draft, people: 9 }, { ...draft, people: 1.5 }, { name: '  ', people: 2 }, { ...draft, people: '' }]) {
    const h = createReservationHarness(), c = factory(h.api);
    c.setDraft(invalid); assert.equal(c.snapshot().canSubmit, false);
    await c.submit(); assert.equal(c.snapshot().phase, 'failed');
    assert.ok(c.snapshot().error); assert.equal(h.control.inspect().writes, 0);
    assert.deepEqual(c.snapshot().draft, invalid);
  }
});
R('R05', 'error', 'reservation 2', '入力エラーから修正して完了', async ({ c, h }) => {
  c.setDraft({ ...draft, people: 0 }); await c.submit();
  c.setDraft({ people: 2 }); assert.equal(c.snapshot().draft.name, draft.name);
  await c.submit(); assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(h.control.inspect().created, 1);
});
R('R06', 'boundary', 'reservation 3', '送信応答待ちの連打を抑止', async ({ c, h, note }) => {
  h.control.plan('reserve', { defer: true }); c.setDraft(draft);
  const first = c.submit(); await tick();
  assert.equal(c.snapshot().phase, 'submitting'); assert.equal(c.snapshot().receipt, null);
  assert.equal(c.snapshot().canSubmit, false); assert.equal(c.snapshot().canRetry, false);
  const second = c.submit(), third = c.retry(); await tick(); note('while pending');
  assert.equal(h.control.inspect().calls.reserve, 1);
  releaseAll(h, 'reserve'); await Promise.all([first, second, third]);
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(h.control.inspect().created, 1);
});
R('R07', 'error', 'reservation 2, retry interface', '確定失敗後の同一意図再試行', async ({ c, h, note }) => {
  h.control.plan('reserve', { result: 'reject' }); c.setDraft(draft); await c.submit(); note('definitive failure');
  const key = c.snapshot().requestKey;
  assert.equal(c.snapshot().phase, 'failed'); assert.deepEqual(c.snapshot().draft, draft);
  assert.equal(c.snapshot().canRetry, true); await c.retry();
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(c.snapshot().requestKey, key);
  assert.equal(h.control.inspect().created, 1);
});
R('R08', 'error', 'reservation retry interface', '確定失敗後の編集は新しい送信意図', async ({ c, h }) => {
  h.control.plan('reserve', { result: 'reject' }); c.setDraft(draft); await c.submit();
  const key = c.snapshot().requestKey; c.setDraft({ people: 3 }); await c.submit();
  assert.equal(c.snapshot().phase, 'succeeded'); assert.notEqual(c.snapshot().requestKey, key);
  assert.equal(c.snapshot().receipt.people, 3); assert.equal(h.control.inspect().created, 1);
});
R('R09', 'error', 'reservation 5', '書込み済み応答不明を照会で解決', async ({ c, h, note }) => {
  h.control.plan('reserve', { result: 'commit-unknown' }); c.setDraft(draft); await c.submit(); note('unknown');
  assert.equal(c.snapshot().phase, 'uncertain'); assert.equal(c.snapshot().receipt, null);
  assert.equal(c.snapshot().canReconcile, true); assert.deepEqual(c.snapshot().draft, draft);
  await c.reconcile(); assert.equal(c.snapshot().phase, 'succeeded');
  assert.equal(h.control.inspect().writes, 1); assert.equal(h.control.inspect().created, 1);
});
R('R10', 'error', 'reservation 5', '書込み済み応答不明を同一key再送', async ({ c, h }) => {
  h.control.plan('reserve', { result: 'commit-unknown' }); c.setDraft(draft); await c.submit();
  const key = c.snapshot().requestKey; assert.equal(c.snapshot().canRetry, true); await c.retry();
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(c.snapshot().requestKey, key);
  assert.equal(h.control.inspect().created, 1); assert.equal(h.control.inspect().deduplicated, 1);
});
R('R11', 'error', 'reservation 5', '照会で未発見でも不明を維持して同一key再試行', async ({ c, h, note }) => {
  h.control.plan('reserve', { result: 'no-commit-unknown' }); c.setDraft(draft); await c.submit();
  const key = c.snapshot().requestKey; await c.reconcile(); note('not found');
  assert.equal(c.snapshot().phase, 'uncertain'); assert.equal(c.snapshot().requestKey, key);
  assert.equal(c.snapshot().canRetry, true); await c.retry();
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(c.snapshot().requestKey, key);
  assert.equal(h.control.inspect().created, 1);
});
R('R12', 'boundary', 'reservation 6', '送信中の取消しをserver取消済みにしない', async ({ c, h }) => {
  h.control.plan('reserve', { defer: true }); c.setDraft(draft); const pending = c.submit(); await tick();
  assert.equal(c.snapshot().canCancel, false); c.cancel(); assert.equal(c.snapshot().phase, 'submitting');
  releaseAll(h, 'reserve'); await pending; assert.equal(c.snapshot().phase, 'succeeded');
});
R('R13', 'boundary', 'reservation 5,6', '結果不明中の編集・取消しで意図を失わない', async ({ c, h }) => {
  h.control.plan('reserve', { result: 'commit-unknown' }); c.setDraft(draft); await c.submit();
  const key = c.snapshot().requestKey; c.setDraft({ name: '変更', people: 8 }); c.cancel();
  assert.equal(c.snapshot().phase, 'uncertain'); assert.equal(c.snapshot().canCancel, false);
  assert.deepEqual(c.snapshot().draft, draft); assert.equal(c.snapshot().requestKey, key);
  await c.reconcile(); assert.equal(c.snapshot().phase, 'succeeded');
});
R('R14', 'normal', 'reservation 6,8', '未送信の破棄と新しい編集の再開', async ({ c, h }) => {
  c.setDraft(draft); assert.equal(c.snapshot().canCancel, true); c.cancel();
  assert.equal(c.snapshot().phase, 'cancelled'); assert.equal(h.control.inspect().writes, 0);
  c.setDraft(draft); await c.submit(); assert.equal(c.snapshot().phase, 'succeeded');
});
R('R15', 'boundary', 'reservation 8', '完了後の連打は無効、新規編集は別予約', async ({ c, h }) => {
  c.setDraft(draft); await c.submit(); const key = c.snapshot().requestKey;
  await c.submit(); await c.retry(); assert.equal(h.control.inspect().writes, 1);
  c.setDraft({ ...draft, people: 3 }); await c.submit();
  assert.equal(c.snapshot().phase, 'succeeded'); assert.notEqual(c.snapshot().requestKey, key);
  assert.equal(h.control.inspect().created, 2);
});
R('R16', 'error', 'reservation 5', '照会失敗でも入力と不明状態を保持', async ({ c, h }) => {
  h.control.plan('reserve', { result: 'commit-unknown' }); c.setDraft(draft); await c.submit();
  h.control.plan('lookup', { result: 'reject' }); await c.reconcile();
  assert.equal(c.snapshot().phase, 'uncertain'); assert.deepEqual(c.snapshot().draft, draft);
  assert.ok(c.snapshot().error); assert.equal(c.snapshot().canReconcile, true);
  await c.reconcile(); assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(h.control.inspect().writes, 1);
});
R('R17', 'boundary', 'reservation reconcile interface', '照会中の再押下・再送を抑止', async ({ c, h }) => {
  h.control.plan('reserve', { result: 'commit-unknown' }); c.setDraft(draft); await c.submit();
  h.control.plan('lookup', { defer: true }); const first = c.reconcile(); await tick();
  assert.equal(c.snapshot().canReconcile, false); assert.equal(c.snapshot().canRetry, false);
  const second = c.reconcile(), third = c.retry(); await tick();
  assert.equal(h.control.inspect().calls.lookup, 1); assert.equal(h.control.inspect().calls.reserve, 1);
  releaseAll(h, 'lookup'); await Promise.all([first, second, third]);
  assert.equal(c.snapshot().phase, 'succeeded');
});
R('R18', 'boundary', 'common snapshot contract', '返却snapshotの変更が内部状態に伝播しない', async ({ c }) => {
  c.setDraft(draft); const view = c.snapshot(); view.draft.name = '外部変更';
  assert.equal(c.snapshot().draft.name, draft.name); await c.submit();
  const done = c.snapshot(); done.receipt.people = 999;
  assert.equal(c.snapshot().receipt.people, 2);
});
R('R19', 'boundary', 'reservation setDraft interface', '送信中の編集を固定', async ({ c, h }) => {
  h.control.plan('reserve', { defer: true }); c.setDraft(draft); const pending = c.submit(); await tick();
  c.setDraft({ name: '別の人', people: 8 }); assert.deepEqual(c.snapshot().draft, draft);
  releaseAll(h, 'reserve'); await pending; assert.equal(c.snapshot().receipt.people, 2);
});
R('R20', 'boundary', 'common wrong-order calls', '初期状態のretry・reconcileは副作用なし', async ({ c, h }) => {
  await c.retry(); await c.reconcile(); assert.equal(h.control.inspect().writes, 0); assert.equal(h.control.inspect().reads, 0);
});

I('I01', 'normal', 'initial snapshot', '初期状態とjobなし操作', async ({ c, h }) => {
  const s = c.snapshot(); validShape(s, 'import'); assert.equal(s.phase, 'idle');
  assert.deepEqual(s.items, []); assert.equal(s.job, null); assert.equal(s.error, null); assert.equal(s.requestKey, null);
  assert.deepEqual(s.progress, { processed: 0, total: 0 }); assert.equal(s.canStart, false);
  await c.poll(); await c.retryFailed(); await c.cancel(); assert.equal(h.control.inspect().writes, 0); assert.equal(h.control.inspect().reads, 0);
});
I('I02', 'boundary', 'import 1', '空選択・重複IDを開始前に拒否', async ({ factory }) => {
  for (const items of [[], [clone(INVENTORY_ITEMS[0]), clone(INVENTORY_ITEMS[0])]]) {
    const h = createImportHarness(), c = factory(h.api); c.setItems(items);
    assert.equal(c.snapshot().canStart, false); await c.start();
    assert.equal(c.snapshot().phase, 'failed'); assert.ok(c.snapshot().error); assert.equal(h.control.inspect().writes, 0);
  }
});
I('I03', 'boundary', 'import 2', '開始応答待ちの重複起動と対象変更を抑止', async ({ c, h }) => {
  h.control.plan('createJob', { defer: true }); c.setItems(clone(INVENTORY_ITEMS));
  const first = c.start(); await tick(); assert.equal(c.snapshot().phase, 'submitting');
  assert.equal(c.snapshot().canStart, false); assert.equal(c.snapshot().job, null);
  c.setItems([clone(INVENTORY_ITEMS[0])]); assert.deepEqual(c.snapshot().items, INVENTORY_ITEMS);
  const second = c.start(); await tick(); assert.equal(h.control.inspect().calls.createJob, 1);
  releaseAll(h, 'createJob'); await Promise.all([first, second]);
  assert.equal(c.snapshot().phase, 'running'); assert.equal(h.control.inspect().created, 1);
});
I('I04', 'normal', 'import 3', '進捗と全件完了をserver結果から表示', async ctx => {
  await beginImport(ctx); const { c, h, note } = ctx; const id = c.snapshot().job.id;
  h.control.completeItem(id, 'a'); await c.poll(); note('one completed');
  assert.equal(c.snapshot().phase, 'running'); assert.deepEqual(c.snapshot().progress, { processed: 1, total: 3 });
  h.control.completeItem(id, 'b'); h.control.completeItem(id, 'c'); await c.poll();
  assert.equal(c.snapshot().phase, 'succeeded'); assert.deepEqual(c.snapshot().progress, { processed: 3, total: 3 });
  assert.ok(c.snapshot().job.results.every(row => row.status === 'succeeded')); assert.equal(h.control.inspect().created, 1);
});
I('I05', 'error', 'import 4', '部分失敗から失敗項目だけを再試行', async ctx => {
  const id = await makePartial(ctx); const { c, h, note } = ctx; note('partial');
  assert.equal(c.snapshot().phase, 'partial'); assert.equal(c.snapshot().canRetryFailed, true);
  await c.retryFailed(); assert.equal(c.snapshot().phase, 'running');
  assert.deepEqual(h.control.inspect().itemAttempts[id], { a: 1, b: 2, c: 1 });
  assert.deepEqual(c.snapshot().progress, { processed: 2, total: 3 });
  h.control.completeItem(id, 'b'); await c.poll(); assert.equal(c.snapshot().phase, 'succeeded');
});
I('I06', 'boundary', 'import retryFailed interface', '部分再試行の応答待ち連打を抑止', async ctx => {
  const id = await makePartial(ctx); const { c, h } = ctx;
  h.control.plan('retryItems', { defer: true }); const first = c.retryFailed(); await tick();
  assert.equal(c.snapshot().canRetryFailed, false); const second = c.retryFailed(); await tick();
  assert.equal(h.control.inspect().calls.retryItems, 1); releaseAll(h, 'retryItems'); await Promise.all([first, second]);
  assert.deepEqual(h.control.inspect().itemAttempts[id], { a: 1, b: 2, c: 1 });
});
I('I07', 'boundary', 'import 5', '取消応答待ち・成功保持・取消し確定', async ctx => {
  await beginImport(ctx); const { c, h, note } = ctx; const id = c.snapshot().job.id;
  h.control.completeItem(id, 'a'); await c.poll(); h.control.plan('cancelJob', { defer: true });
  const first = c.cancel(); await tick(); note('cancel pending');
  assert.equal(c.snapshot().phase, 'cancelling'); assert.equal(c.snapshot().canCancel, false);
  assert.equal(h.control.inspect().jobs[0].phase, 'running'); const second = c.cancel(); await tick();
  assert.equal(h.control.inspect().calls.cancelJob, 1); releaseAll(h, 'cancelJob'); await Promise.all([first, second]);
  assert.equal(c.snapshot().phase, 'cancelled');
  assert.deepEqual(c.snapshot().job.results.map(row => row.status), ['succeeded', 'cancelled', 'cancelled']);
});
I('I08', 'boundary', 'import 5', '取消しと全件成功の競合は実結果を採用', async ctx => {
  await beginImport(ctx); const { c, h } = ctx; const id = c.snapshot().job.id;
  h.control.plan('cancelJob', { defer: true }); const pending = c.cancel(); await tick();
  for (const item of INVENTORY_ITEMS) h.control.completeItem(id, item.id);
  releaseAll(h, 'cancelJob'); await pending;
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(h.control.inspect().cancelEffects, 0);
});
I('I09', 'boundary', 'import 6', '取消し後の古いpollでrunningへ戻らない', async ctx => {
  await beginImport(ctx); const { c, h, note } = ctx; const old = clone(c.snapshot().job);
  h.control.plan('getJob', { defer: true, result: 'snapshot', value: old }); const poll = c.poll(); await tick();
  await c.cancel(); assert.equal(c.snapshot().phase, 'cancelled'); const version = c.snapshot().job.version;
  releaseAll(h, 'getJob'); await poll; note('stale read delivered');
  assert.equal(c.snapshot().phase, 'cancelled'); assert.equal(c.snapshot().job.version, version);
});
I('I10', 'error', 'import poll interface', 'poll失敗でも既知結果を保持し再取得', async ctx => {
  await beginImport(ctx); const { c, h } = ctx; const id = c.snapshot().job.id;
  h.control.completeItem(id, 'a'); await c.poll(); const known = clone(c.snapshot().job);
  h.control.plan('getJob', { result: 'reject' }); await c.poll();
  assert.deepEqual(c.snapshot().job, known); assert.ok(c.snapshot().error); assert.equal(c.snapshot().canPoll, true);
  h.control.completeItem(id, 'b'); h.control.completeItem(id, 'c'); await c.poll();
  assert.equal(c.snapshot().phase, 'succeeded');
});
I('I11', 'normal', 'import 7', '再訪で既存jobと部分結果を復元し書込まない', async ctx => {
  const id = await makePartial(ctx); const { h, factory } = ctx;
  const reopened = factory(h.api); const before = h.control.inspect().writes;
  await reopened.resume(id); const s = reopened.snapshot(); validShape(s, 'import');
  assert.equal(s.phase, 'partial'); assert.equal(s.job.id, id); assert.deepEqual(s.items, INVENTORY_ITEMS);
  assert.equal(s.canRetryFailed, true); assert.equal(h.control.inspect().writes, before); assert.equal(h.control.inspect().created, 1);
});
I('I12', 'error', 'import 7,8', '不存在jobの説明と正しいjobへの復帰', async ({ c, h }) => {
  await c.resume('missing'); assert.equal(c.snapshot().phase, 'failed'); assert.ok(c.snapshot().error);
  assert.equal(h.control.inspect().writes, 0);
  const job = await h.api.createJob({ key: 'external-setup', items: clone(INVENTORY_ITEMS) });
  const before = h.control.inspect().writes; await c.resume(job.id);
  assert.equal(c.snapshot().phase, 'running'); assert.equal(c.snapshot().job.id, job.id); assert.equal(h.control.inspect().writes, before);
});
I('I13', 'error', 'common definitive failure; import 2', '開始の確定失敗後に対象を保持して再開', async ({ c, h }) => {
  h.control.plan('createJob', { result: 'reject' }); c.setItems(clone(INVENTORY_ITEMS)); await c.start();
  assert.equal(c.snapshot().phase, 'failed'); assert.deepEqual(c.snapshot().items, INVENTORY_ITEMS); assert.ok(c.snapshot().error);
  await c.start(); assert.equal(c.snapshot().phase, 'running'); assert.equal(h.control.inspect().created, 1);
});
I('I14', 'error', 'common unknown outcome; import 2', '開始結果不明を確定失敗にせずjobを重複生成しない', async ({ c, h, note }) => {
  h.control.plan('createJob', { result: 'commit-unknown' }); c.setItems(clone(INVENTORY_ITEMS)); await c.start(); note('unknown start');
  assert.equal(c.snapshot().phase, 'uncertain'); assert.ok(c.snapshot().error);
  const key = c.snapshot().requestKey; await c.start();
  assert.equal(h.control.inspect().created, 1); assert.equal(c.snapshot().requestKey, key);
  assert.ok(['uncertain', 'running'].includes(c.snapshot().phase));
});
I('I15', 'error', 'import 5; common errors', '取消し確定失敗を取消済みにせず復帰', async ctx => {
  await beginImport(ctx); const { c, h } = ctx;
  h.control.plan('cancelJob', { result: 'reject' }); await c.cancel();
  assert.notEqual(c.snapshot().phase, 'cancelled'); assert.ok(c.snapshot().error);
  assert.equal(h.control.inspect().jobs[0].phase, 'running'); await c.poll(); await c.cancel();
  assert.equal(c.snapshot().phase, 'cancelled');
});
I('I16', 'error', 'import 5; common unknown outcome', '取消し結果不明をpollで確定', async ctx => {
  await beginImport(ctx); const { c, h } = ctx;
  h.control.plan('cancelJob', { result: 'commit-unknown' }); await c.cancel();
  assert.equal(c.snapshot().phase, 'uncertain'); assert.ok(c.snapshot().error);
  await c.poll(); assert.equal(c.snapshot().phase, 'cancelled'); assert.equal(h.control.inspect().cancelEffects, 1);
});
I('I17', 'boundary', 'import 3,6', '成功後の再開始・取消し・再試行で副作用を追加しない', async ctx => {
  await beginImport(ctx); const { c, h } = ctx; const id = c.snapshot().job.id;
  for (const item of INVENTORY_ITEMS) h.control.completeItem(id, item.id); await c.poll();
  const before = h.control.inspect().writes; await c.start(); await c.cancel(); await c.retryFailed();
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(h.control.inspect().writes, before);
});
I('I18', 'boundary', 'common snapshot contract', 'job・items・progressのsnapshotを独立させる', async ctx => {
  await beginImport(ctx); const { c } = ctx; const original = clone(c.snapshot());
  const view = c.snapshot(); view.items[0].name = '外部変更'; view.job.results[0].status = 'succeeded'; view.progress.processed = 999;
  assert.deepEqual(c.snapshot(), original);
});
I('I19', 'boundary', 'import version interface', '別jobへの復帰でversion比較を混同しない', async ctx => {
  await beginImport(ctx); const { c, h } = ctx; const id = c.snapshot().job.id;
  for (const item of INVENTORY_ITEMS) h.control.completeItem(id, item.id); await c.poll();
  const other = await h.api.createJob({ key: 'other-job', items: [clone(INVENTORY_ITEMS[0])] });
  assert.ok(other.version < c.snapshot().job.version); const before = h.control.inspect().writes;
  await c.resume(other.id); assert.equal(c.snapshot().job.id, other.id); assert.equal(c.snapshot().phase, 'running');
  assert.deepEqual(c.snapshot().items, [INVENTORY_ITEMS[0]]); assert.equal(h.control.inspect().writes, before);
});
I('I20', 'boundary', 'import resume interface', '既存job読込み中の状態と書込みゼロ', async ({ c, h }) => {
  const job = await h.api.createJob({ key: 'resume-setup', items: clone(INVENTORY_ITEMS) });
  h.control.plan('getJob', { defer: true }); const before = h.control.inspect().writes;
  const pending = c.resume(job.id); await tick(); assert.equal(c.snapshot().phase, 'loading'); assert.equal(c.snapshot().canStart, false);
  releaseAll(h, 'getJob'); await pending; assert.equal(c.snapshot().phase, 'running'); assert.equal(h.control.inspect().writes, before);
});

async function hashFile(file) { return createHash('sha256').update(await readFile(file)).digest('hex'); }
async function deadline(promise, milliseconds = 1500) {
  let timer;
  try { return await Promise.race([promise, new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('case did not settle within 1500ms')), milliseconds); })]); }
  finally { clearTimeout(timer); }
}

const result = {
  schema: 'b-behavioral-comparison/v1', recorded_at: new Date().toISOString(), runtime: process.version,
  evaluator: 'root authored deterministic shared requirement tests; not independent or blind',
  scope: 'controller behavior with in-memory API; no DOM, rendering, keyboard or real network verification',
  limitations: ['One generated sample per arm; model revision and seed not exposed.', 'Shared filesystem is not an enforced holdout.', 'I14 checks unknown-outcome safety only; it does not prove recovery affordance or liveness.', 'API exactly-once behavior is a simulation contract, not a production guarantee.'],
  input_hashes: {}, arms: {}, formal_gate: 'HOLD',
};
for (const relative of ['evaluate.mjs', 'shared/tasks.md', 'shared/api.mjs', 'shared/visual-lock.md']) result.input_hashes[relative] = await hashFile(path.join(here, relative));
for (const arm of ['baseline', 'candidate']) {
  const record = { modules: {}, cases: [], summary: {} }; result.arms[arm] = record;
  let factories;
  try {
    const reservationPath = path.join(here, arm, 'reservation.mjs'), importPath = path.join(here, arm, 'import-job.mjs');
    record.modules['reservation.mjs'] = await hashFile(reservationPath); record.modules['import-job.mjs'] = await hashFile(importPath);
    factories = { reservation: (await import(pathToFileURL(reservationPath))).createReservationController, import: (await import(pathToFileURL(importPath))).createImportController };
    assert.equal(typeof factories.reservation, 'function'); assert.equal(typeof factories.import, 'function');
  } catch (error) { record.load_error = { name: error.name, message: error.message }; }
  for (const spec of cases) {
    const row = { id: spec.id, task: spec.task, category: spec.category, requirement: spec.requirement, title: spec.title, classification: 'interaction', status: 'not_run', observations: [] };
    record.cases.push(row);
    if (!factories || record.load_error) { row.reason = 'controller module unavailable'; continue; }
    const h = spec.task === 'reservation' ? createReservationHarness() : createImportHarness();
    let c;
    try {
      c = factories[spec.task](h.api);
      const note = label => row.observations.push({ label, snapshot: clone(c.snapshot()) });
      await deadline(Promise.resolve().then(() => spec.run({ c, h, note, factory: factories[spec.task] })));
      row.status = 'pass';
    } catch (error) {
      row.status = 'fail'; row.failure = { name: error.name, message: error.message, expected: error.expected, actual: error.actual, operator: error.operator };
    } finally {
      try { row.final_snapshot = c?.snapshot(); } catch (error) { row.snapshot_error = error.message; }
      row.server_trace = h.control.inspect();
    }
  }
  for (const task of ['reservation', 'import', 'all']) {
    const subset = record.cases.filter(row => task === 'all' || row.task === task);
    record.summary[task] = Object.fromEntries(['pass', 'fail', 'not_run'].map(status => [status, subset.filter(row => row.status === status).length]));
  }
}
await mkdir(output, { recursive: true });
await writeFile(path.join(output, 'comparison.json'), JSON.stringify(result, null, 2) + '\n');
const lines = ['# 共通controller実行比較', '', '自己管理の模擬API検査。独立blind評価、ブラウザー検証、実利用者の完了率ではない。正式gate: **HOLD**。', '', '| ケース | 分類 | 検査 | baseline | candidate |', '|---|---|---|---|---|'];
for (let n = 0; n < cases.length; n++) lines.push(`| ${cases[n].id} | ${cases[n].category} | ${cases[n].title} | ${result.arms.baseline.cases[n].status} | ${result.arms.candidate.cases[n].status} |`);
lines.push('', '## 集計', '', '```json', JSON.stringify(Object.fromEntries(Object.entries(result.arms).map(([arm, value]) => [arm, value.summary])), null, 2), '```', '', '各assertion、最終snapshot、API request/response・副作用回数はcomparison.jsonへ保存。', '件数は選定したscenarioの結果であり、母集団の成功率やSkillの因果効果を推定しない。', 'I14は結果不明時の安全性だけを検査するため、復帰操作の存在は別レビューが必要。', '');
await writeFile(path.join(output, 'comparison.md'), lines.join('\n'));
console.log(JSON.stringify(Object.fromEntries(Object.entries(result.arms).map(([arm, value]) => [arm, value.summary])), null, 2));
process.exitCode = Object.values(result.arms).some(arm => arm.cases.some(row => row.status !== 'pass')) ? 1 : 0;
