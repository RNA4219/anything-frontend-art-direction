// 通常デモのserver進行・保存のみを扱う。controllerと表示部品はcontrolを参照しない。
const STORAGE_KEY = 'workshop-inventory-baseline-demo-v1';

export async function createDemoSession(reservationHarness, importHarness, storage) {
  const timers = new Map();
  let lastJobId = null;
  let storageAvailable = !!storage;
  let restored = null;
  try {
    const raw = storage?.getItem(STORAGE_KEY);
    if (raw) restored = JSON.parse(raw);
  } catch {
    storageAvailable = false;
  }

  // fixtureはメモリ上にあるため、再読み込みでは保存した通常操作を順番どおり復元する。
  // 復元の間、UI controllerはまだ作られておらず、新規取込み操作は受け付けない。
  if (restored?.format === 1 && Array.isArray(restored.jobs) && Array.isArray(restored.history)) {
    try {
      for (const receipt of restored.receipts ?? []) {
        await reservationHarness.api.reserve({ key: receipt.key, draft: { name: receipt.name, people: receipt.people } });
      }
      const jobs = new Map(restored.jobs.map(job => [job.id, job]));
      for (const event of restored.history) {
        if (event.type === 'created') {
          const saved = jobs.get(event.jobId);
          await importHarness.api.createJob({ key: saved.key, items: saved.results.map(({ id, name }) => ({ id, name })) });
        } else if (event.type === 'item_completed') {
          importHarness.control.completeItem(event.jobId, event.itemId, event.result);
        } else if (event.type === 'retried') {
          await importHarness.api.retryItems({ jobId: event.jobId, key: `restore-${event.jobId}-${event.version}`, itemIds: event.itemIds });
        } else if (event.type === 'cancel_acknowledged') {
          await importHarness.api.cancelJob(event.jobId);
        }
      }
      lastJobId = typeof restored.lastJobId === 'string' ? restored.lastJobId : null;
    } catch {
      // 壊れた保存情報から「取込み完了」を作らない。復帰操作で取得できる状態だけ表示する。
      storageAvailable = false;
      lastJobId = null;
    }
  }

  function persist() {
    if (!storageAvailable) return;
    const { jobs, jobHistory } = importHarness.control.inspect();
    const { receipts } = reservationHarness.control.inspect();
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify({ format: 1, receipts, jobs, history: jobHistory, lastJobId }));
    } catch {
      storageAvailable = false;
    }
  }

  function schedule(job) {
    if (job.phase !== 'running') return;
    job.results.filter(row => row.status === 'pending').forEach((row, index) => {
      const key = `${job.id}:${job.generation}:${row.id}`;
      if (timers.has(key)) return;
      const timer = setTimeout(() => {
        timers.delete(key);
        importHarness.control.completeItem(job.id, row.id, 'succeeded');
        persist();
      }, 1100 + index * 800);
      // Nodeでの自己確認を不必要に待たせない。ブラウザーのtimerにはunrefがない。
      timer?.unref?.();
      timers.set(key, timer);
    });
  }

  for (const job of importHarness.control.inspect().jobs) schedule(job);

  return Object.freeze({
    get lastJobId() { return lastJobId; },
    get storageAvailable() { return storageAvailable; },
    afterAction(job = null) {
      if (job) {
        lastJobId = job.id;
        schedule(job);
      }
      persist();
    },
    dispose() {
      for (const timer of timers.values()) clearTimeout(timer);
      timers.clear();
      persist();
    },
  });
}
