import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';
import { createReservationHarness, createImportHarness, INVENTORY_ITEMS } from '../shared/api.mjs';
import { createReservationController } from './reservation.mjs';
import { createImportController } from './import-job.mjs';
import { createDemoClient } from './demo-client.mjs';
import { createDemoServer } from './demo-server.mjs';

const cases = [];
const draft = { name: '山田 太郎', people: 2 };
const items = () => INVENTORY_ITEMS.map(item => ({ ...item }));
let steps = [];
const trace = (action, controller, harness) => steps.push({ action, snapshot: controller.snapshot(), server: harness.control.inspect() });
const pending = (harness, method) => harness.control.pending(method)[0].id;
async function test(id, category, description, run) {
  steps = [];
  try {
    await run();
    cases.push({ id, category, description, status: 'pass', steps });
  } catch (error) {
    cases.push({ id, category, description, status: 'fail', error: error.stack, steps });
  }
}

await test('R01', 'normal', '予約の初期状態と独立したsnapshot', async () => {
  const h = createReservationHarness(), c = createReservationController(h.api);
  assert.deepEqual(c.snapshot(), { phase: 'idle', draft: { name: '', people: '' }, receipt: null, error: null,
    requestKey: null, canSubmit: false, canRetry: false, canReconcile: false, canCancel: false });
  const returned = c.setDraft(draft); returned.draft.name = '別の名前';
  assert.equal(c.snapshot().draft.name, draft.name);
  await c.submit(); const receipt = c.snapshot(); receipt.receipt.name = '改変';
  assert.equal(c.snapshot().receipt.name, draft.name);
  trace('入力→送信→receipt保持', c, h);
});

await test('R02', 'boundary', '人数0・1・8・9・小数、空白名を検証する', async () => {
  const h = createReservationHarness(), c = createReservationController(h.api);
  for (const value of [0, 9, 1.5, '', ' ', 'abc']) {
    c.setDraft({ name: draft.name, people: value });
    assert.equal(c.snapshot().canSubmit, false);
    assert.equal((await c.submit()).phase, 'failed');
    assert.ok(c.snapshot().error.fields.people);
  }
  c.setDraft({ name: ' \t\n ', people: 1 }); await c.submit();
  assert.ok(c.snapshot().error.fields.name); assert.equal(h.control.inspect().writes, 0);
  for (const value of ['1', '8']) {
    c.setDraft({ name: ' 山田 太郎 ', people: value });
    await c.submit(); assert.equal(c.snapshot().phase, 'succeeded');
    assert.equal(typeof c.snapshot().receipt.people, 'number');
  }
  assert.equal(h.control.inspect().created, 2);
  trace('境界入力→修正→成功', c, h);
});

await test('R03', 'boundary', '応答待ちの連打・編集・取消しを抑止する', async () => {
  const h = createReservationHarness(), c = createReservationController(h.api);
  h.control.plan('reserve', { defer: true }); c.setDraft(draft);
  const sending = c.submit(); const original = c.snapshot();
  assert.equal(original.phase, 'submitting');
  await c.submit(); await c.retry(); await c.reconcile(); c.cancel(); c.setDraft({ people: 8 });
  assert.deepEqual(c.snapshot().draft, draft); assert.equal(h.control.inspect().writes, 1);
  trace('送信待ちに操作を連打', c, h);
  h.control.release(pending(h, 'reserve')); await sending;
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(h.control.inspect().created, 1);
  trace('応答を受領', c, h);
});

await test('R04', 'error', '確定失敗から同じ意図を再試行し成功後の再送を防ぐ', async () => {
  const h = createReservationHarness(), c = createReservationController(h.api);
  h.control.plan('reserve', { result: 'reject' }); c.setDraft(draft);
  await c.submit(); assert.equal(c.snapshot().phase, 'failed');
  assert.equal(c.snapshot().canRetry, true); assert.equal(c.snapshot().canCancel, true);
  const key = c.snapshot().requestKey; await c.retry();
  assert.equal(c.snapshot().requestKey, key); assert.equal(c.snapshot().phase, 'succeeded');
  await c.submit(); await c.retry(); c.cancel();
  assert.equal(h.control.inspect().calls.reserve, 2);
  c.setDraft(draft); await c.submit();
  assert.notEqual(c.snapshot().requestKey, key); assert.equal(h.control.inspect().created, 2);
  trace('拒否→同一再試行→新しい予約', c, h);
});

await test('R05', 'error', 'commit後の応答不明を照会して一件の確定へ復帰する', async () => {
  const h = createReservationHarness(), c = createReservationController(h.api);
  h.control.plan('reserve', { result: 'commit-unknown' }); c.setDraft(draft);
  await c.submit(); assert.equal(c.snapshot().phase, 'uncertain');
  c.setDraft({ people: 8 }); c.cancel(); assert.deepEqual(c.snapshot().draft, draft);
  assert.equal(c.snapshot().canCancel, false);
  await c.reconcile(); assert.equal(c.snapshot().phase, 'succeeded');
  assert.equal(h.control.inspect().created, 1); assert.equal(h.control.inspect().writes, 1);
  trace('結果不明→照会→確定', c, h);
});

await test('R06', 'error', '見つからない照会でも同じkeyと入力を保持する', async () => {
  const h = createReservationHarness(), c = createReservationController(h.api);
  h.control.plan('reserve', { result: 'no-commit-unknown' }); c.setDraft(draft);
  await c.submit(); const key = c.snapshot().requestKey;
  await c.reconcile(); assert.equal(c.snapshot().phase, 'uncertain');
  assert.equal(c.snapshot().canRetry, true); assert.equal(c.snapshot().canCancel, false);
  await c.retry(); assert.equal(c.snapshot().requestKey, key); assert.equal(c.snapshot().phase, 'succeeded');
  assert.equal(h.control.inspect().created, 1);
  const requests = h.control.inspect().requests.filter(row => row.method === 'reserve');
  assert.deepEqual(requests[0].args, requests[1].args);
  trace('結果不明→not-found→同一再試行', c, h);
});

await test('R07', 'error', '不明な送信の後に再試行・照会が拒否されても未実行とはしない', async () => {
  const h = createReservationHarness(), c = createReservationController(h.api);
  h.control.plan('reserve', { result: 'commit-unknown' }, { result: 'reject' }); c.setDraft(draft);
  await c.submit(); await c.retry(); assert.equal(c.snapshot().phase, 'uncertain');
  h.control.plan('lookup', { result: 'reject' }); await c.reconcile();
  assert.equal(c.snapshot().phase, 'uncertain'); assert.equal(c.snapshot().canCancel, false);
  await c.reconcile(); assert.equal(c.snapshot().phase, 'succeeded');
  assert.equal(h.control.inspect().created, 1);
  trace('不明→再送拒否→照会拒否→照会成功', c, h);
});

await test('R08', 'boundary', '未送信破棄、確定失敗後の修正、新しい入力のkey分離', async () => {
  const h = createReservationHarness(), c = createReservationController(h.api);
  c.setDraft(draft); c.cancel(); await c.submit(); assert.equal(h.control.inspect().writes, 0);
  assert.equal(c.snapshot().phase, 'cancelled');
  c.setDraft(draft); h.control.plan('reserve', { result: 'reject' }); await c.submit();
  const old = c.snapshot().requestKey; c.setDraft({ people: 8 }); await c.submit();
  assert.notEqual(c.snapshot().requestKey, old); assert.equal(c.snapshot().receipt.people, 8);
  trace('破棄→編集→拒否→修正→成功', c, h);
});

await test('I01', 'boundary', '初期状態・空配列・重複ID・誤順序の操作', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  assert.deepEqual(c.snapshot().progress, { processed: 0, total: 0 });
  assert.equal(c.snapshot().phase, 'idle');
  await c.poll(); await c.retryFailed(); await c.cancel();
  await c.start(); assert.equal(c.snapshot().phase, 'failed');
  c.setItems([]); await c.start();
  c.setItems([items()[0], items()[0]]); await c.start();
  assert.equal(h.control.inspect().writes, 0); assert.equal(h.control.inspect().reads, 0);
  const selected = items(); c.setItems(selected); selected[0].name = '改変';
  assert.equal(c.snapshot().items[0].name, '青いノート');
  trace('無効な選択と誤順序の操作', c, h);
});

await test('I02', 'boundary', '開始待ちの連打と選択変更を抑止する', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); h.control.plan('createJob', { defer: true });
  const starting = c.start(); assert.equal(c.snapshot().phase, 'submitting');
  await c.start(); await c.retryFailed(); await c.cancel(); c.setItems([]);
  assert.equal(c.snapshot().items.length, 3); assert.equal(h.control.inspect().writes, 1);
  trace('開始応答待ち', c, h);
  h.control.release(pending(h, 'createJob')); await starting;
  assert.equal(c.snapshot().phase, 'running'); assert.equal(h.control.inspect().created, 1);
  const snap = c.snapshot(); snap.job.results[0].name = '改変'; snap.progress.total = 99;
  assert.equal(c.snapshot().job.results[0].name, '青いノート'); assert.equal(c.snapshot().progress.total, 3);
  trace('job受領', c, h);
});

await test('I03', 'normal', '部分失敗から失敗項目だけを再試行して全成功へ進む', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  h.control.completeItem(id, 'a'); h.control.completeItem(id, 'b', 'failed'); await c.poll();
  assert.equal(c.snapshot().phase, 'running'); assert.equal(c.snapshot().progress.processed, 2);
  h.control.completeItem(id, 'c'); await c.poll(); assert.equal(c.snapshot().phase, 'partial');
  h.control.plan('retryItems', { defer: true }); const retrying = c.retryFailed();
  assert.equal(c.snapshot().phase, 'submitting'); await c.retryFailed();
  assert.equal(h.control.inspect().calls.retryItems, 1);
  trace('部分失敗→再試行応答待ち', c, h);
  h.control.release(pending(h, 'retryItems')); await retrying;
  assert.equal(c.snapshot().phase, 'running'); assert.equal(c.snapshot().progress.processed, 2);
  assert.deepEqual(h.control.inspect().itemAttempts[id], { a: 1, b: 2, c: 1 });
  h.control.completeItem(id, 'b'); await c.poll(); assert.equal(c.snapshot().phase, 'succeeded');
  const writes = h.control.inspect().writes; await c.start(); await c.retryFailed(); await c.cancel();
  assert.equal(h.control.inspect().writes, writes);
  trace('失敗項目だけの完了', c, h);
});

await test('I04', 'error', '進捗読取りが失敗しても既知の結果を保持する', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  h.control.completeItem(id, 'a'); await c.poll(); const known = c.snapshot().job;
  h.control.plan('getJob', { result: 'reject' }); await c.poll();
  assert.deepEqual(c.snapshot().job, known); assert.equal(c.snapshot().phase, 'running');
  assert.ok(c.snapshot().error); assert.equal(c.snapshot().canPoll, true);
  trace('読取り拒否後の保持', c, h);
});

await test('I05', 'boundary', '取消し応答後に古いpollが届いても処理中へ戻らない', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  h.control.completeItem(id, 'a'); await c.poll(); const stale = c.snapshot().job;
  h.control.plan('getJob', { result: 'snapshot', value: stale, defer: true });
  const polling = c.poll(); const read = pending(h, 'getJob');
  h.control.plan('cancelJob', { defer: true }); const cancelling = c.cancel();
  assert.equal(c.snapshot().phase, 'cancelling'); await c.cancel();
  assert.equal(h.control.inspect().calls.cancelJob, 1); trace('取消し応答待ち', c, h);
  h.control.release(pending(h, 'cancelJob')); await cancelling;
  assert.equal(c.snapshot().phase, 'cancelled');
  h.control.release(read); await polling; assert.equal(c.snapshot().phase, 'cancelled');
  assert.equal(c.snapshot().job.results[0].status, 'succeeded');
  assert.deepEqual(c.snapshot().job.results.slice(1).map(row => row.status), ['cancelled', 'cancelled']);
  trace('取消し確定→古い応答', c, h);
});

await test('I06', 'boundary', '取消しより先に全成功した場合は成功という実結果を示す', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  h.control.plan('cancelJob', { defer: true }); const cancelling = c.cancel();
  for (const item of items()) h.control.completeItem(id, item.id);
  h.control.release(pending(h, 'cancelJob')); await cancelling;
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(c.snapshot().progress.processed, 3);
  trace('取消し待ち中に全成功', c, h);
});

await test('I07', 'boundary', '再試行前の古い進捗で再試行後のjobを巻き戻さない', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  for (const item of items()) h.control.completeItem(id, item.id, item.id === 'b' ? 'failed' : 'succeeded');
  await c.poll(); const old = c.snapshot().job;
  h.control.plan('getJob', { result: 'snapshot', value: old, defer: true });
  const polling = c.poll(); const read = pending(h, 'getJob');
  await c.retryFailed(); h.control.release(read); await polling;
  assert.equal(c.snapshot().job.generation, 1); assert.equal(c.snapshot().phase, 'running');
  assert.equal(c.snapshot().job.results[1].status, 'pending');
  trace('再試行後→古い部分結果', c, h);
});

await test('I08', 'normal', 'controller再作成後に既存jobを読取りだけで復帰する', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  h.control.completeItem(id, 'a'); const writes = h.control.inspect().writes;
  const restored = createImportController(h.api); h.control.plan('getJob', { defer: true });
  const loading = restored.resume(id); assert.equal(restored.snapshot().phase, 'loading');
  h.control.release(pending(h, 'getJob')); await loading;
  assert.equal(restored.snapshot().phase, 'running'); assert.deepEqual(restored.snapshot().items, items());
  assert.equal(restored.snapshot().job.results[0].status, 'succeeded');
  assert.equal(h.control.inspect().writes, writes); assert.equal(h.control.inspect().created, 1);
  trace('保持したjobIdで復帰', restored, h);
});

await test('I09', 'boundary', '別jobへの復帰でversionを混同せず古いjob応答を無視する', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const first = c.snapshot().job.id;
  for (const item of items()) h.control.completeItem(first, item.id);
  await c.poll(); const old = c.snapshot().job;
  const other = await h.api.createJob({ key: 'self-check-second-job', items: [{ id: 'x', name: '既存の別項目' }] });
  assert.ok(other.version < old.version);
  h.control.plan('getJob', { result: 'snapshot', value: old, defer: true }); const polling = c.poll(); const read = pending(h, 'getJob');
  await c.resume(other.id); h.control.release(read); await polling;
  assert.equal(c.snapshot().job.id, other.id); assert.equal(c.snapshot().phase, 'running');
  assert.deepEqual(c.snapshot().items, [{ id: 'x', name: '既存の別項目' }]);
  trace('別job読取り→前jobの遅い応答', c, h);
});

await test('I10', 'error', '存在しないjobIdは失敗説明を返し新規jobを作らない', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  await c.resume('missing-job'); assert.equal(c.snapshot().phase, 'failed');
  assert.equal(c.snapshot().error.code, 'NOT_FOUND'); assert.equal(h.control.inspect().writes, 0);
  c.setItems(items()); await c.start(); assert.equal(c.snapshot().phase, 'running');
  trace('見つからないjob→選択して新規開始', c, h);
});

await test('I11', 'error', '開始結果不明から同じkeyで復帰しjobを増やさない', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); h.control.plan('createJob', { result: 'commit-unknown' });
  await c.start(); assert.equal(c.snapshot().phase, 'uncertain'); const key = c.snapshot().requestKey;
  c.setItems([]); assert.equal(c.snapshot().items.length, 3); await c.start();
  assert.equal(c.snapshot().requestKey, key); assert.equal(c.snapshot().phase, 'running');
  assert.equal(h.control.inspect().created, 1);
  trace('開始結果不明→同一再試行', c, h);
});

await test('I12', 'error', '再試行結果不明の照会と、次batchのkey分離', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  for (const item of items()) h.control.completeItem(id, item.id, item.id === 'b' ? 'failed' : 'succeeded');
  await c.poll(); h.control.plan('retryItems', { result: 'commit-unknown' });
  await c.retryFailed(); assert.equal(c.snapshot().phase, 'uncertain');
  const firstKey = c.snapshot().requestKey; await c.poll(); assert.equal(c.snapshot().phase, 'running');
  h.control.completeItem(id, 'b', 'failed'); await c.poll(); await c.retryFailed();
  assert.notEqual(c.snapshot().requestKey, firstKey); assert.equal(c.snapshot().job.generation, 2);
  assert.deepEqual(h.control.inspect().itemAttempts[id], { a: 1, b: 3, c: 1 });
  trace('再試行不明→照会→再度の部分失敗→次batch', c, h);
});

await test('I13', 'error', '取消し応答不明を成功済み項目の保持とともに照会する', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  h.control.completeItem(id, 'a'); await c.poll(); h.control.plan('cancelJob', { result: 'commit-unknown' });
  await c.cancel(); assert.equal(c.snapshot().phase, 'uncertain'); await c.poll();
  assert.equal(c.snapshot().phase, 'cancelled'); assert.equal(c.snapshot().job.results[0].status, 'succeeded');
  trace('取消し結果不明→照会', c, h);
});

await test('I14', 'boundary', '取消し応答が失敗しても、先に照会で確定した全成功を維持する', async () => {
  const h = createImportHarness(), c = createImportController(h.api);
  c.setItems(items()); await c.start(); const id = c.snapshot().job.id;
  h.control.plan('getJob', { defer: true }); const polling = c.poll(); const read = pending(h, 'getJob');
  h.control.plan('cancelJob', { defer: true, result: 'reject' }); const cancelling = c.cancel();
  for (const item of items()) h.control.completeItem(id, item.id);
  h.control.release(read); await polling; assert.equal(c.snapshot().phase, 'cancelling');
  h.control.release(pending(h, 'cancelJob')); await cancelling;
  assert.equal(c.snapshot().phase, 'succeeded'); assert.equal(c.snapshot().progress.processed, 3);
  trace('全成功の照会応答→取消しの拒否応答', c, h);
});

await test('H01', 'normal', 'Node HTTP経由の送受信・公開画面配信・新しいclientからの既存job復帰', async () => {
  const server = createDemoServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  try {
    const client = createDemoClient(new URL(`${origin}/api/`));
    const r = createReservationController(client.reservation); r.setDraft(draft); await r.submit();
    assert.equal(r.snapshot().phase, 'succeeded');
    const c = createImportController(client.inventory); c.setItems(items()); await c.start();
    assert.equal(c.snapshot().phase, 'running'); const id = c.snapshot().job.id;
    const newClient = createDemoClient(new URL(`${origin}/api/`));
    const restored = createImportController(newClient.inventory); await restored.resume(id);
    assert.equal(restored.snapshot().job.id, id); assert.deepEqual(restored.snapshot().items, items());
    for (const path of ['/candidate/index.html', '/shared/api.mjs', '/candidate/ui.mjs', '/candidate/demo-client.mjs']) {
      const response = await fetch(origin + path); assert.equal(response.status, 200); await response.text();
    }
    const hidden = await fetch(origin + '/api/inventory/inspect', { method: 'POST', body: '{}' });
    assert.equal(hidden.status, 404); await hidden.text();
    steps.push({ action: 'HTTP送信→新clientのresume→同一job', reservation: r.snapshot(), resumed: restored.snapshot(), note: 'ブラウザー操作ではなくNode fetchによる輸送層確認。' });
  } finally {
    await new Promise(resolve => server.close(resolve));
  }
});

const report = {
  scope: '自作controllerと共通公開APIの自己確認。共通評価テストは未参照。画面操作は未実行。',
  runtime: process.version,
  results: cases,
  summary: { executed: cases.length, passed: cases.filter(c => c.status === 'pass').length, failed: cases.filter(c => c.status === 'fail').length },
  ui: { status: 'not_run', reason: '指示によりブラウザー操作は禁止。1280px/390px、Enter、フォーカス、読み上げ、実フォントは未実行。' },
};
await writeFile(new URL('./self-check-results.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
const log = cases.map(c => `${c.status.toUpperCase()} ${c.id} ${c.description}${c.error ? '\n' + c.error : ''}`).join('\n');
await writeFile(new URL('./self-check.log', import.meta.url), log + '\n' + JSON.stringify(report.summary) + '\n');
console.log(log);
console.log(JSON.stringify(report.summary));
if (report.summary.failed) process.exitCode = 1;
