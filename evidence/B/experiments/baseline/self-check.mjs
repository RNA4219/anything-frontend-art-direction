// 共有の評価用ファイルは使わず、この実装の公開操作を確認する独自の自己確認。
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFile } from 'node:fs/promises';
import { createReservationHarness, createImportHarness, INVENTORY_ITEMS, PHASES } from '../shared/api.mjs';
import { createReservationController } from './reservation.mjs';
import { createImportController } from './import-job.mjs';
import { createDemoSession } from './demo-runtime.mjs';

const draft = { name: '山田 太郎', people: 2 };
const makeR = () => {
  const harness = createReservationHarness();
  return { c: createReservationController(harness.api), ...harness };
};
const makeI = () => {
  const harness = createImportHarness();
  return { c: createImportController(harness.api), ...harness };
};
const release = (control, method) => control.release(control.pending(method)[0].id);

test('予約：初期値と独立snapshot', () => {
  const { c } = makeR();
  assert.deepEqual(c.snapshot(), {
    phase: 'idle', draft: { name: '', people: '' }, receipt: null, error: null, requestKey: null,
    canSubmit: false, canRetry: false, canReconcile: false, canCancel: false,
  });
  const changed = c.snapshot(); changed.draft.name = '変更';
  assert.equal(c.snapshot().draft.name, '');
});

for (const people of [0, 9, 1.5, '', ' ', '-1', 'abc']) {
  test(`予約：人数 ${JSON.stringify(people)} は書込みなし`, async () => {
    const { c, control } = makeR(); c.setDraft({ ...draft, people });
    assert.equal(c.snapshot().canSubmit, false);
    const result = await c.submit();
    assert.equal(result.phase, 'failed'); assert.ok(result.error.fields.people);
    assert.equal(control.inspect().writes, 0);
  });
}

for (const people of [1, 8, '2']) {
  test(`予約：人数 ${JSON.stringify(people)} と名前の正規化`, async () => {
    const { c, control } = makeR(); c.setDraft({ name: ' 山田 太郎 ', people });
    const result = await c.submit();
    assert.equal(result.phase, 'succeeded');
    assert.equal(result.receipt.name, '山田 太郎');
    assert.equal(result.receipt.people, Number(people));
    assert.equal(control.inspect().created, 1);
  });
}

test('予約：空白名を修正して再送できる', async () => {
  const { c, control } = makeR(); c.setDraft({ name: '　 ', people: 2 });
  assert.equal((await c.submit()).phase, 'failed');
  assert.equal(control.inspect().writes, 0);
  c.setDraft({ name: draft.name });
  assert.equal((await c.submit()).phase, 'succeeded');
});

test('予約：応答待ちの連打・編集・破棄を抑止', async () => {
  const { c, control } = makeR(); c.setDraft(draft);
  control.plan('reserve', { defer: true });
  const pending = c.submit();
  assert.equal(c.snapshot().phase, 'submitting');
  await c.submit(); await c.retry(); await c.reconcile();
  c.setDraft({ name: '別人' }); c.cancel();
  assert.deepEqual(c.snapshot().draft, draft);
  assert.equal(control.inspect().writes, 1);
  release(control, 'reserve');
  assert.equal((await pending).phase, 'succeeded');
  await c.submit(); await c.retry();
  assert.equal(control.inspect().created, 1);
  c.setDraft(draft); await c.submit();
  assert.equal(control.inspect().created, 2);
});

test('予約：確定失敗の再試行は同じkey・入力', async () => {
  const { c, control } = makeR(); c.setDraft(draft);
  control.plan('reserve', { result: 'reject' });
  const failed = await c.submit();
  assert.equal(failed.phase, 'failed'); assert.ok(failed.canRetry); assert.ok(failed.canCancel);
  await c.retry();
  const requests = control.inspect().requests.filter(row => row.method === 'reserve');
  assert.deepEqual(requests[0].args, requests[1].args);
  assert.equal(c.snapshot().phase, 'succeeded');
});

test('予約：確定失敗から入力を変えた送信は新しいkey', async () => {
  const { c, control } = makeR(); c.setDraft(draft);
  control.plan('reserve', { result: 'reject' });
  const first = await c.submit();
  c.setDraft({ people: 3 }); const second = await c.submit();
  assert.notEqual(first.requestKey, second.requestKey);
  assert.equal(second.receipt.people, 3);
});

test('予約：完了後の応答不明を照会で回復', async () => {
  const { c, control } = makeR(); c.setDraft(draft);
  control.plan('reserve', { result: 'commit-unknown' });
  const uncertain = await c.submit();
  assert.equal(uncertain.phase, 'uncertain'); assert.ok(uncertain.canRetry); assert.ok(uncertain.canReconcile);
  assert.equal(uncertain.canCancel, false);
  c.cancel(); c.setDraft({ people: 7 }); await c.submit();
  assert.deepEqual(c.snapshot().draft, draft);
  assert.equal((await c.reconcile()).phase, 'succeeded');
  assert.equal(control.inspect().created, 1); assert.equal(control.inspect().writes, 1);
});

test('予約：見つからない照会後も同じkeyで再試行', async () => {
  const { c, control } = makeR(); c.setDraft(draft);
  control.plan('reserve', { result: 'no-commit-unknown' });
  const before = await c.submit();
  const missing = await c.reconcile();
  assert.equal(missing.phase, 'uncertain'); assert.ok(missing.canRetry);
  assert.equal(missing.canCancel, false);
  const success = await c.retry();
  assert.equal(success.requestKey, before.requestKey); assert.equal(control.inspect().created, 1);
});

test('予約：結果不明の後の確定失敗でも最初の結果不明を維持', async () => {
  const { c, control } = makeR(); c.setDraft(draft);
  control.plan('reserve', { result: 'commit-unknown' }, { result: 'reject' });
  await c.submit();
  assert.equal((await c.retry()).phase, 'uncertain');
  assert.equal(c.cancel().phase, 'uncertain');
  assert.equal((await c.reconcile()).phase, 'succeeded');
});

test('予約：照会中の連打と照会失敗を処理', async () => {
  const { c, control } = makeR(); c.setDraft(draft);
  control.plan('reserve', { result: 'no-commit-unknown' }); await c.submit();
  control.plan('lookup', { defer: true, result: 'reject' });
  const pending = c.reconcile();
  assert.equal(c.snapshot().canRetry, false); assert.equal(c.snapshot().canReconcile, false);
  await c.reconcile(); await c.retry(); release(control, 'lookup');
  assert.equal((await pending).phase, 'uncertain'); assert.equal(control.inspect().calls.lookup, 1);
});

test('予約：未送信入力の破棄後に新しい編集を開始できる', async () => {
  const { c, control } = makeR(); c.setDraft(draft);
  assert.equal(c.cancel().phase, 'cancelled');
  await c.submit(); assert.equal(control.inspect().writes, 0);
  c.setDraft(draft); assert.equal((await c.submit()).phase, 'succeeded');
});

test('取込み：初期値、空選択、重複IDを検証', async () => {
  const { c, control } = makeI();
  assert.deepEqual(c.snapshot(), {
    phase: 'idle', items: [], job: null, error: null, requestKey: null,
    progress: { processed: 0, total: 0 }, canStart: false, canPoll: false, canRetryFailed: false, canCancel: false,
  });
  await c.poll(); await c.cancel(); await c.retryFailed();
  assert.equal(control.inspect().reads, 0); assert.equal(control.inspect().writes, 0);
  assert.equal((await c.start()).phase, 'failed');
  c.setItems([]); assert.equal((await c.start()).phase, 'failed');
  c.setItems([INVENTORY_ITEMS[0], INVENTORY_ITEMS[0]]);
  assert.equal(c.snapshot().canStart, false); assert.equal((await c.start()).phase, 'failed');
  assert.equal(control.inspect().writes, 0);
});

test('取込み：開始連打を抑止して全成功を取得', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS);
  control.plan('createJob', { defer: true }); const pending = c.start();
  assert.equal(c.snapshot().phase, 'submitting');
  c.setItems([]); await c.start(); await c.cancel(); await c.retryFailed();
  assert.equal(c.snapshot().items.length, 3); assert.equal(control.inspect().writes, 1);
  release(control, 'createJob'); const running = await pending;
  assert.equal(running.phase, 'running');
  for (const item of INVENTORY_ITEMS) control.completeItem(running.job.id, item.id);
  assert.equal(c.snapshot().phase, 'running');
  assert.equal((await c.poll()).phase, 'succeeded');
  await c.start(); assert.equal(control.inspect().created, 1);
});

test('取込み：部分失敗と再試行で成功項目を再処理しない', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS);
  const { job } = await c.start();
  control.completeItem(job.id, 'a', 'succeeded');
  control.completeItem(job.id, 'b', 'failed');
  control.completeItem(job.id, 'c', 'succeeded');
  const partial = await c.poll();
  assert.equal(partial.phase, 'partial'); assert.deepEqual(partial.progress, { processed: 3, total: 3 });
  assert.ok(partial.canRetryFailed);
  control.plan('retryItems', { defer: true }); const retry = c.retryFailed();
  assert.equal(c.snapshot().phase, 'submitting'); assert.equal(c.snapshot().canRetryFailed, false);
  await c.retryFailed(); release(control, 'retryItems');
  const running = await retry;
  assert.equal(running.phase, 'running'); assert.equal(running.progress.processed, 2);
  assert.deepEqual(control.inspect().itemAttempts[job.id], { a: 1, b: 2, c: 1 });
  control.completeItem(job.id, 'b', 'succeeded');
  assert.equal((await c.poll()).phase, 'succeeded');
});

test('取込み：取消し応答前は確定させず、遅いpollを無視', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS);
  const running = await c.start();
  control.completeItem(running.job.id, 'a'); await c.poll();
  const old = c.snapshot().job;
  control.plan('getJob', { defer: true, result: 'snapshot', value: old });
  const oldPoll = c.poll();
  control.plan('cancelJob', { defer: true }); const pending = c.cancel();
  assert.equal(c.snapshot().phase, 'cancelling'); assert.equal(c.snapshot().canCancel, false);
  await c.cancel(); c.setItems([]);
  assert.equal(c.snapshot().items.length, 3);
  release(control, 'cancelJob'); const cancelled = await pending;
  assert.equal(cancelled.phase, 'cancelled'); assert.equal(cancelled.job.results[0].status, 'succeeded');
  release(control, 'getJob'); await oldPoll;
  assert.equal(c.snapshot().phase, 'cancelled');
  assert.equal(control.inspect().calls.cancelJob, 1);
});

test('取込み：中止要求中に全件完了した場合は成功を表示', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS);
  const { job } = await c.start();
  control.plan('cancelJob', { defer: true }); const pending = c.cancel();
  for (const row of INVENTORY_ITEMS) control.completeItem(job.id, row.id);
  release(control, 'cancelJob');
  assert.equal((await pending).phase, 'succeeded');
});

test('取込み：確定した成功を古い読取りで戻さない', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS);
  const running = await c.start();
  for (const row of INVENTORY_ITEMS) control.completeItem(running.job.id, row.id);
  await c.poll();
  control.plan('getJob', { result: 'snapshot', value: running.job });
  assert.equal((await c.poll()).phase, 'succeeded');
});

test('取込み：poll失敗でも既知の結果・進捗を保持', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS); const { job } = await c.start();
  control.completeItem(job.id, 'a'); const before = await c.poll();
  control.plan('getJob', { result: 'reject' }); const after = await c.poll();
  assert.equal(after.phase, 'running'); assert.deepEqual(after.job, before.job); assert.deepEqual(after.progress, before.progress);
  assert.ok(after.error); assert.ok(after.canPoll);
});

test('取込み：新しいcontrollerで復帰し、読み戻しは書込みを増やさない', async () => {
  const { c, api, control } = makeI(); c.setItems(INVENTORY_ITEMS); const { job } = await c.start();
  control.completeItem(job.id, 'a');
  const next = createImportController(api);
  control.plan('getJob', { defer: true }); const restore = next.resume(job.id);
  assert.equal(next.snapshot().phase, 'loading');
  release(control, 'getJob'); const resumed = await restore;
  assert.equal(resumed.phase, 'running'); assert.deepEqual(resumed.items, INVENTORY_ITEMS);
  assert.equal(resumed.progress.processed, 1); assert.equal(control.inspect().writes, 1);
  assert.equal((await next.resume('missing-job')).phase, 'failed');
  assert.equal(next.snapshot().job, null); assert.ok(next.snapshot().error.message);
});

test('取込み：別jobへの復帰でversionを混同しない', async () => {
  const { c, api, control } = makeI(); c.setItems(INVENTORY_ITEMS); const first = await c.start();
  for (const item of INVENTORY_ITEMS) control.completeItem(first.job.id, item.id);
  await c.poll();
  const second = await api.createJob({ key: 'separate-job', items: [INVENTORY_ITEMS[0]] });
  assert.ok(c.snapshot().job.version > second.version);
  const resumed = await c.resume(second.id);
  assert.equal(resumed.job.id, second.id); assert.equal(resumed.phase, 'running'); assert.equal(resumed.items.length, 1);
});

test('取込み：別jobへ移った後の旧pollを無視', async () => {
  const { c, api, control } = makeI(); c.setItems(INVENTORY_ITEMS); const first = await c.start();
  const second = await api.createJob({ key: 'other-job', items: [INVENTORY_ITEMS[1]] });
  control.plan('getJob', { defer: true, result: 'snapshot', value: first.job }); const pending = c.poll();
  await c.resume(second.id); release(control, 'getJob'); await pending;
  assert.equal(c.snapshot().job.id, second.id); assert.deepEqual(c.snapshot().items, [INVENTORY_ITEMS[1]]);
});

test('取込み：開始結果不明から同じkeyで回復', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS);
  control.plan('createJob', { result: 'commit-unknown' }); const uncertain = await c.start();
  assert.equal(uncertain.phase, 'uncertain'); assert.ok(uncertain.canStart);
  c.setItems([]); await c.resume('different-job');
  assert.equal(c.snapshot().phase, 'uncertain');
  const running = await c.start();
  assert.equal(running.phase, 'running'); assert.equal(running.requestKey, uncertain.requestKey);
  assert.equal(control.inspect().created, 1);
});

test('取込み：失敗項目の再試行結果不明を同じkeyで再送', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS); const { job } = await c.start();
  for (const row of INVENTORY_ITEMS) control.completeItem(job.id, row.id, row.id === 'b' ? 'failed' : 'succeeded');
  await c.poll();
  control.plan('retryItems', { result: 'commit-unknown' }); const uncertain = await c.retryFailed();
  assert.equal(uncertain.phase, 'uncertain'); assert.ok(uncertain.canRetryFailed);
  await c.retryFailed();
  assert.equal(control.inspect().retryBatches, 1);
  assert.deepEqual(control.inspect().itemAttempts[job.id], { a: 1, b: 2, c: 1 });
  const calls = control.inspect().requests.filter(row => row.method === 'retryItems');
  assert.deepEqual(calls[0].args, calls[1].args);
});

test('取込み：取消し結果不明はpollで確認', async () => {
  const { c, control } = makeI(); c.setItems(INVENTORY_ITEMS); await c.start();
  control.plan('cancelJob', { result: 'commit-unknown' });
  assert.equal((await c.cancel()).phase, 'uncertain');
  assert.equal((await c.poll()).phase, 'cancelled');
});

test('取込み：snapshotの結果・選択を外部変更しても内部に影響しない', async () => {
  const { c } = makeI(); const items = INVENTORY_ITEMS.map(item => ({ ...item })); c.setItems(items);
  items[0].name = '変更'; const current = await c.start();
  current.items[0].name = '別'; current.job.results[0].status = 'succeeded'; current.progress.processed = 99;
  assert.equal(c.snapshot().items[0].name, '青いノート'); assert.equal(c.snapshot().job.results[0].status, 'pending');
  assert.equal(c.snapshot().progress.processed, 0); assert.ok(PHASES.includes(c.snapshot().phase));
});

test('通常デモ：保存済みjobを新しいfixtureへ復元できる', async () => {
  const values = new Map(); const storage = { getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value) };
  const r1 = createReservationHarness(), i1 = createImportHarness();
  const demo1 = await createDemoSession(r1, i1, storage);
  const { id } = await i1.api.createJob({ key: 'persisted-job', items: INVENTORY_ITEMS });
  i1.control.completeItem(id, 'a', 'succeeded'); i1.control.completeItem(id, 'b', 'failed'); i1.control.completeItem(id, 'c', 'succeeded');
  await i1.api.retryItems({ jobId: id, key: 'persisted-retry', itemIds: ['b'] });
  i1.control.completeItem(id, 'b', 'succeeded');
  const original = await i1.api.getJob(id); demo1.afterAction(original); demo1.dispose();
  const r2 = createReservationHarness(), i2 = createImportHarness();
  const demo2 = await createDemoSession(r2, i2, storage);
  assert.equal(demo2.lastJobId, id);
  const c = createImportController(i2.api); assert.deepEqual((await c.resume(id)).job, original);
  demo2.dispose();
});

test('静的UI：指定文言、相対API import、色・書体・狭幅指定', async () => {
  const html = await readFile(new URL('./index.html', import.meta.url), 'utf8');
  for (const phrase of ['ワークショップ参加予約', '参加する人の名前と人数を入力してください。', '在庫データ取込み', '選んだ3件の在庫データを取り込みます。', '青いノート', '赤い鉛筆', '白い封筒', '#172323', '#f6f2e9', '#245b48', 'Yu Mincho', 'Hiragino Mincho ProN', '../shared/api.mjs']) {
    assert.ok(html.includes(phrase), phrase);
  }
  assert.ok(html.includes('minmax(0,1fr)')); assert.ok(html.includes('@media(max-width:760px)'));
  assert.ok(html.includes('role="status"')); assert.ok(html.includes('aria-describedby='));
  assert.ok(!html.includes('http://') && !html.includes('https://'));
});
