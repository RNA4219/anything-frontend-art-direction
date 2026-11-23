/** Deterministic, in-memory experiment API. It is not a production backend. */
export const PHASES = Object.freeze([
  'idle', 'editing', 'loading', 'submitting', 'running', 'partial',
  'succeeded', 'failed', 'uncertain', 'cancelling', 'cancelled',
]);

export const INVENTORY_ITEMS = Object.freeze([
  Object.freeze({ id: 'a', name: '青いノート' }),
  Object.freeze({ id: 'b', name: '赤い鉛筆' }),
  Object.freeze({ id: 'c', name: '白い封筒' }),
]);

const copy = value => structuredClone(value);
const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);
const nonempty = value => typeof value === 'string' && value.trim().length > 0;

export class SimulationError extends Error {
  constructor(code, message, outcome = 'definitive', fields = undefined) {
    super(message);
    this.name = 'SimulationError';
    this.code = code;
    this.outcome = outcome;
    if (fields !== undefined) this.fields = fields;
  }
}

function invalid(code, message, fields) {
  throw new SimulationError(code, message, 'definitive', fields);
}

function keyRequired(key) {
  if (!nonempty(key)) invalid('INVALID_KEY', '操作識別子が必要です。');
}

function reservationDraft(draft) {
  const fields = {};
  if (!draft || !nonempty(draft.name)) fields.name = '名前を入力してください。';
  if (!draft || !Number.isInteger(draft.people) || draft.people < 1 || draft.people > 8) {
    fields.people = '参加人数は1〜8の整数で入力してください。';
  }
  if (Object.keys(fields).length) invalid('VALIDATION', '入力内容を確認してください。', fields);
  return { name: draft.name.trim(), people: draft.people };
}

function importItems(items) {
  if (!Array.isArray(items) || items.length === 0) {
    invalid('INVALID_ITEMS', '取り込む項目を選んでください。');
  }
  if (items.some(item => !item || !nonempty(item.id) || !nonempty(item.name))) {
    invalid('INVALID_ITEMS', '項目にはIDと名前が必要です。');
  }
  if (new Set(items.map(item => item.id)).size !== items.length) {
    invalid('INVALID_ITEMS', '項目IDを重複させないでください。');
  }
  return items.map(({ id, name }) => ({ id, name }));
}

/**
 * Plans are test controls, deliberately excluded from the object given to a controller.
 * result: ok | reject | commit-unknown | no-commit-unknown | snapshot.
 * A deferred request runs its server effect only when release() is called.
 */
function transport(operations) {
  const queues = new Map(Object.keys(operations).map(method => [method, []]));
  const pending = new Map();
  const requests = [];
  const events = [];
  const calls = Object.fromEntries(Object.keys(operations).map(method => [method, 0]));
  let serial = 0;
  let tick = 0;
  let reads = 0;
  let writes = 0;

  function record(event) { events.push({ sequence: ++tick, ...copy(event) }); }

  function normalize(method, value = {}) {
    if (!Object.hasOwn(operations, method)) throw new TypeError(`Unknown operation: ${method}`);
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new TypeError('Invalid plan');
    const plan = { result: 'ok', defer: false, ...copy(value) };
    if (!['ok', 'reject', 'commit-unknown', 'no-commit-unknown', 'snapshot'].includes(plan.result)) {
      throw new TypeError(`Unknown plan result: ${plan.result}`);
    }
    if (plan.result === 'snapshot' && operations[method].write) {
      throw new TypeError('snapshot plans are only permitted for read operations');
    }
    if (plan.result === 'snapshot' && !Object.hasOwn(plan, 'value')) {
      throw new TypeError('snapshot plans require value');
    }
    return plan;
  }

  function settle(id, override = {}) {
    const entry = pending.get(id);
    if (!entry) throw new Error(`Request is not pending: ${id}`);
    const plan = normalize(entry.request.method, { ...entry.plan, ...override });
    pending.delete(id);
    const request = entry.request;
    try {
      if (plan.result === 'reject') {
        throw new SimulationError(plan.code ?? 'UNAVAILABLE', plan.message ?? '処理に失敗しました。', 'definitive');
      }
      if (plan.result === 'no-commit-unknown') {
        throw new SimulationError('TIMEOUT', '処理結果を確認できませんでした。', 'unknown');
      }
      const result = plan.result === 'snapshot'
        ? copy(plan.value)
        : operations[request.method].run(copy(request.args));
      if (plan.result === 'commit-unknown') {
        throw new SimulationError('TIMEOUT', '処理結果を確認できませんでした。', 'unknown');
      }
      request.status = 'resolved';
      request.result = copy(result);
      record({ type: 'response', id, method: request.method, status: 'resolved', result });
      entry.resolve(copy(result));
    } catch (error) {
      const failure = {
        code: error.code ?? 'INTERNAL', message: error.message,
        outcome: error.outcome ?? 'definitive',
        ...(error.fields ? { fields: copy(error.fields) } : {}),
      };
      request.status = 'rejected';
      request.error = failure;
      record({ type: 'response', id, method: request.method, status: 'rejected', error: failure });
      entry.reject(error);
    }
  }

  const api = Object.fromEntries(Object.keys(operations).map(method => [method, args => {
    const plan = queues.get(method).shift() ?? normalize(method);
    const id = `request-${String(++serial).padStart(4, '0')}`;
    const request = { id, method, args: copy(args), status: 'pending' };
    calls[method]++;
    if (operations[method].write) writes++; else reads++;
    requests.push(request);
    record({ type: 'request', id, method, args: request.args });
    const promise = new Promise((resolve, reject) => {
      pending.set(id, { request, plan, resolve, reject });
    });
    if (!plan.defer) queueMicrotask(() => { if (pending.has(id)) settle(id); });
    return promise;
  }]));

  return {
    api: Object.freeze(api),
    control: {
      plan(method, ...values) {
        const normalized = values.map(value => normalize(method, value));
        queues.get(method).push(...normalized);
      },
      pending(method) {
        return [...pending.values()]
          .map(entry => entry.request)
          .filter(request => method === undefined || request.method === method)
          .map(copy);
      },
      release: settle,
      inspect() { return copy({ calls, reads, writes, requests, events }); },
    },
  };
}

export function createReservationHarness() {
  const receipts = new Map();
  let created = 0;
  let deduplicated = 0;
  const wire = transport({
    reserve: {
      write: true,
      run({ key, draft } = {}) {
        keyRequired(key);
        const normalized = reservationDraft(draft);
        if (receipts.has(key)) {
          const existing = receipts.get(key);
          if (!same({ name: existing.name, people: existing.people }, normalized)) {
            invalid('KEY_CONFLICT', '同じ操作識別子を別の入力には使えません。');
          }
          deduplicated++;
          return existing;
        }
        const receipt = {
          id: `reservation-${String(++created).padStart(4, '0')}`,
          key, ...normalized, status: 'confirmed',
        };
        receipts.set(key, receipt);
        return receipt;
      },
    },
    lookup: {
      write: false,
      run(key) {
        keyRequired(key);
        return { found: receipts.has(key), receipt: receipts.get(key) ?? null };
      },
    },
  });
  return {
    api: wire.api,
    control: {
      ...wire.control,
      inspect() {
        return { ...wire.control.inspect(), created, deduplicated, receipts: copy([...receipts.values()]) };
      },
    },
  };
}

export function createImportHarness() {
  const jobs = new Map();
  const creationKeys = new Map();
  const retryKeys = new Map();
  const jobHistory = [];
  const itemAttempts = {};
  let serial = 0;
  let sequence = 0;
  let retryBatches = 0;
  let cancelAcknowledgements = 0;
  let cancelEffects = 0;

  function event(job, type, detail = {}) {
    jobHistory.push({ sequence: ++sequence, jobId: job.id, type, version: job.version, ...copy(detail) });
  }
  function getJob(id) {
    if (!jobs.has(id)) invalid('NOT_FOUND', '処理が見つかりません。');
    return jobs.get(id);
  }
  function update(job) {
    job.progress = {
      processed: job.results.filter(row => row.status === 'succeeded' || row.status === 'failed').length,
      total: job.results.length,
    };
    if (job.results.some(row => row.status === 'pending')) job.phase = 'running';
    else if (job.results.some(row => row.status === 'cancelled')) job.phase = 'cancelled';
    else if (job.results.some(row => row.status === 'failed')) job.phase = 'partial';
    else job.phase = 'succeeded';
    job.version++;
  }

  const wire = transport({
    createJob: {
      write: true,
      run({ key, items } = {}) {
        keyRequired(key);
        const normalized = importItems(items);
        if (creationKeys.has(key)) {
          const existing = creationKeys.get(key);
          if (!same(existing.items, normalized)) invalid('KEY_CONFLICT', '操作識別子が別の入力に使われています。');
          return getJob(existing.id);
        }
        const id = `job-${String(++serial).padStart(4, '0')}`;
        const job = {
          id, key, phase: 'running', version: 1, generation: 0,
          progress: { processed: 0, total: normalized.length },
          results: normalized.map(item => ({ ...item, status: 'pending', error: null })),
        };
        jobs.set(id, job);
        creationKeys.set(key, { id, items: normalized });
        itemAttempts[id] = Object.fromEntries(normalized.map(({ id: itemId }) => [itemId, 1]));
        event(job, 'created', { itemIds: normalized.map(item => item.id) });
        return job;
      },
    },
    getJob: { write: false, run: id => getJob(id) },
    retryItems: {
      write: true,
      run({ jobId, key, itemIds } = {}) {
        keyRequired(key);
        const job = getJob(jobId);
        if (!Array.isArray(itemIds) || !itemIds.length || new Set(itemIds).size !== itemIds.length) {
          invalid('INVALID_RETRY', '再試行する項目を重複なく指定してください。');
        }
        const normalizedIds = [...itemIds].sort();
        const intent = { jobId, itemIds: normalizedIds };
        if (retryKeys.has(key)) {
          if (!same(retryKeys.get(key), intent)) invalid('KEY_CONFLICT', '操作識別子が別の再試行に使われています。');
          return job;
        }
        if (job.phase !== 'partial' || itemIds.some(id => !job.results.some(row => row.id === id && row.status === 'failed'))) {
          invalid('INVALID_RETRY', '失敗した項目だけを再試行できます。');
        }
        retryKeys.set(key, intent);
        for (const row of job.results) {
          if (itemIds.includes(row.id)) {
            row.status = 'pending';
            row.error = null;
            itemAttempts[jobId][row.id]++;
          }
        }
        job.generation++;
        retryBatches++;
        update(job);
        event(job, 'retried', { itemIds: normalizedIds });
        return job;
      },
    },
    cancelJob: {
      write: true,
      run(id) {
        const job = getJob(id);
        const pendingRows = job.results.filter(row => row.status === 'pending');
        cancelAcknowledgements++;
        if (pendingRows.length) {
          for (const row of pendingRows) row.status = 'cancelled';
          cancelEffects++;
          update(job);
        }
        event(job, 'cancel_acknowledged', { cancelledItemIds: pendingRows.map(row => row.id) });
        return job;
      },
    },
  });

  return {
    api: wire.api,
    control: {
      ...wire.control,
      completeItem(jobId, itemId, result = 'succeeded') {
        if (!['succeeded', 'failed'].includes(result)) throw new TypeError('Unknown item result');
        const job = getJob(jobId);
        const row = job.results.find(item => item.id === itemId);
        if (!row) invalid('NOT_FOUND', '項目が見つかりません。');
        if (row.status !== 'pending') {
          event(job, 'completion_ignored', { itemId, result });
          return false;
        }
        row.status = result;
        row.error = result === 'failed' ? '取り込みに失敗しました。' : null;
        update(job);
        event(job, 'item_completed', { itemId, result });
        return true;
      },
      inspect() {
        return {
          ...wire.control.inspect(), jobs: copy([...jobs.values()]), jobHistory: copy(jobHistory),
          created: jobs.size, retryBatches, cancelAcknowledgements, cancelEffects,
          itemAttempts: copy(itemAttempts),
        };
      },
    },
  };
}
