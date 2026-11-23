import test from 'node:test';
import assert from 'node:assert/strict';
import { createReservationHarness, createImportHarness, INVENTORY_ITEMS } from './api.mjs';

const draft = { name: '山田 太郎', people: 2 };

test('reservation: same-key retries produce one receipt; key conflicts do not write', async () => {
  const { api, control } = createReservationHarness();
  const one = await api.reserve({ key: 'intent-1', draft });
  const two = await api.reserve({ key: 'intent-1', draft });
  assert.deepEqual(two, one);
  await assert.rejects(api.reserve({ key: 'intent-1', draft: { ...draft, people: 3 } }), { code: 'KEY_CONFLICT' });
  assert.equal(control.inspect().created, 1);
  assert.equal(control.inspect().deduplicated, 1);
  assert.equal(control.inspect().writes, 3);
});

test('reservation: validation checks empty names, both integer bounds, and fractions', async () => {
  const { api, control } = createReservationHarness();
  for (const people of [0, 9, 1.5, '2']) {
    await assert.rejects(api.reserve({ key: `invalid-${people}`, draft: { ...draft, people } }), { code: 'VALIDATION' });
  }
  await assert.rejects(api.reserve({ key: 'blank', draft: { name: '  ', people: 2 } }), { code: 'VALIDATION' });
  await api.reserve({ key: 'min', draft: { ...draft, people: 1 } });
  await api.reserve({ key: 'max', draft: { ...draft, people: 8 } });
  assert.equal(control.inspect().created, 2);
});

test('reservation: identical timeout errors cover commit and no-commit outcomes', async () => {
  const { api, control } = createReservationHarness();
  control.plan('reserve', { result: 'commit-unknown' }, { result: 'no-commit-unknown' });
  await assert.rejects(api.reserve({ key: 'committed', draft }), { code: 'TIMEOUT', outcome: 'unknown' });
  await assert.rejects(api.reserve({ key: 'absent', draft }), { code: 'TIMEOUT', outcome: 'unknown' });
  assert.equal((await api.lookup('committed')).found, true);
  assert.deepEqual(await api.lookup('absent'), { found: false, receipt: null });
  await api.reserve({ key: 'committed', draft });
  assert.equal(control.inspect().created, 1);
  assert.equal(control.inspect().reads, 2);
});

test('deferred effects, reordering, and inspection cannot mutate server state', async () => {
  const { api, control } = createReservationHarness();
  control.plan('reserve', { defer: true }, { defer: true });
  const first = api.reserve({ key: 'one', draft });
  const second = api.reserve({ key: 'two', draft });
  assert.equal(control.inspect().created, 0);
  const [a, b] = control.pending('reserve');
  a.args.draft.people = 999;
  control.release(b.id);
  await second;
  assert.equal(control.inspect().created, 1);
  control.release(a.id);
  assert.equal((await first).people, 2);
  const observed = control.inspect();
  observed.receipts[0].name = 'mutation';
  assert.equal((await api.lookup('two')).receipt.name, draft.name);
  assert.throws(() => control.release(a.id), /not pending/);
});

test('import: processing, failed-subset retry, and retry dedupe preserve successful work', async () => {
  const { api, control } = createImportHarness();
  const initial = await api.createJob({ key: 'batch-1', items: INVENTORY_ITEMS });
  control.completeItem(initial.id, 'a', 'succeeded');
  control.completeItem(initial.id, 'b', 'failed');
  control.completeItem(initial.id, 'c', 'succeeded');
  const partial = await api.getJob(initial.id);
  assert.equal(partial.phase, 'partial');
  assert.deepEqual(partial.progress, { processed: 3, total: 3 });
  await assert.rejects(api.retryItems({ jobId: initial.id, key: 'bad', itemIds: ['a', 'b'] }), { code: 'INVALID_RETRY' });
  const retry = { jobId: initial.id, key: 'retry-1', itemIds: ['b'] };
  const restarted = await api.retryItems(retry);
  assert.equal(restarted.phase, 'running');
  assert.deepEqual(restarted.progress, { processed: 2, total: 3 });
  await api.retryItems(retry);
  assert.deepEqual(control.inspect().itemAttempts[initial.id], { a: 1, b: 2, c: 1 });
  assert.equal(control.inspect().retryBatches, 1);
  control.completeItem(initial.id, 'b', 'succeeded');
  assert.equal((await api.getJob(initial.id)).phase, 'succeeded');
});

test('import: cancel changes server state only on acknowledgement and preserves completed items', async () => {
  const { api, control } = createImportHarness();
  const job = await api.createJob({ key: 'cancel-1', items: INVENTORY_ITEMS });
  control.completeItem(job.id, 'a', 'succeeded');
  control.plan('cancelJob', { defer: true });
  const cancel = api.cancelJob(job.id);
  assert.equal(control.inspect().jobs[0].phase, 'running');
  control.release(control.pending('cancelJob')[0].id);
  const cancelled = await cancel;
  assert.equal(cancelled.phase, 'cancelled');
  assert.deepEqual(cancelled.results.map(row => row.status), ['succeeded', 'cancelled', 'cancelled']);
  assert.equal(control.completeItem(job.id, 'b', 'succeeded'), false);
  assert.equal((await api.getJob(job.id)).phase, 'cancelled');
  assert.equal(control.inspect().cancelEffects, 1);
});

test('import: successful completion can win the race against cancellation', async () => {
  const { api, control } = createImportHarness();
  const job = await api.createJob({ key: 'race', items: INVENTORY_ITEMS });
  control.plan('cancelJob', { defer: true });
  const cancel = api.cancelJob(job.id);
  for (const item of INVENTORY_ITEMS) control.completeItem(job.id, item.id);
  control.release(control.pending('cancelJob')[0].id);
  assert.equal((await cancel).phase, 'succeeded');
  assert.equal(control.inspect().cancelEffects, 0);
});

test('import: stale read can arrive after a newer result without changing server state', async () => {
  const { api, control } = createImportHarness();
  const job = await api.createJob({ key: 'stale', items: INVENTORY_ITEMS });
  control.plan('getJob', { defer: true, result: 'snapshot', value: job });
  const oldPoll = api.getJob(job.id);
  await api.cancelJob(job.id);
  const current = await api.getJob(job.id);
  control.release(control.pending('getJob')[0].id);
  const old = await oldPoll;
  assert.equal(old.phase, 'running');
  assert.equal(current.phase, 'cancelled');
  assert.ok(old.version < current.version);
  assert.equal(control.inspect().jobs[0].phase, 'cancelled');
});

test('import: reading an existing job never starts new work; invalid inputs have no effects', async () => {
  const { api, control } = createImportHarness();
  for (const items of [[], [INVENTORY_ITEMS[0], INVENTORY_ITEMS[0]], [{ id: '', name: 'x' }]]) {
    await assert.rejects(api.createJob({ key: 'invalid', items }), { code: 'INVALID_ITEMS' });
  }
  const job = await api.createJob({ key: 'valid', items: INVENTORY_ITEMS });
  await api.createJob({ key: 'valid', items: INVENTORY_ITEMS });
  const writesBeforeRead = control.inspect().writes;
  assert.deepEqual(await api.getJob(job.id), job);
  await assert.rejects(api.getJob('missing'), { code: 'NOT_FOUND' });
  assert.equal(control.inspect().writes, writesBeforeRead);
  assert.equal(control.inspect().created, 1);
  assert.deepEqual(control.inspect().itemAttempts[job.id], { a: 1, b: 1, c: 1 });
});
