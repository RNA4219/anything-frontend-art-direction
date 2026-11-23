import { copy, errorInfo, isUnknown, operationKey } from './common.mjs';

function validationError(items) {
  if (!items.length) return { code: 'INVALID_ITEMS', message: '取り込む項目を選んでください。' };
  if (items.some(item => !item || typeof item.id !== 'string' || !item.id.trim()
    || typeof item.name !== 'string' || !item.name.trim())) {
    return { code: 'INVALID_ITEMS', message: '項目の名前と識別情報を確認してください。' };
  }
  if (new Set(items.map(item => item.id)).size !== items.length) {
    return { code: 'INVALID_ITEMS', message: '同じ項目を重複して選択することはできません。' };
  }
  return null;
}

export function createImportController(api) {
  const state = { phase: 'idle', items: [], job: null, error: null, requestKey: null };
  let context = 0;
  let revision = 0;
  let reader = null;
  let writer = null;
  let createIntent = null;
  let retryIntent = null;
  let cancelUnknown = false;

  function snapshot() {
    const available = !writer && state.phase !== 'loading';
    const failedIds = state.job?.results.filter(row => row.status === 'failed').map(row => row.id) ?? [];
    return copy({
      ...state,
      progress: state.job?.progress ?? { processed: 0, total: state.items.length },
      canStart: available && !state.job && !validationError(state.items)
        && ['idle', 'editing', 'failed', 'uncertain'].includes(state.phase),
      canPoll: available && !!state.job && !reader,
      canRetryFailed: available && !!state.job && state.job.phase === 'partial' && failedIds.length > 0
        && !cancelUnknown,
      canCancel: available && !!state.job && state.job.phase === 'running' && state.phase === 'running',
    });
  }

  function setItems(items) {
    if (writer || state.phase === 'loading' || state.job?.phase === 'running'
      || createIntent?.unknown || retryIntent?.unknown || cancelUnknown) return snapshot();
    context++;
    revision++;
    reader = null;
    state.items = copy(items);
    state.job = null;
    state.phase = 'editing';
    state.error = null;
    state.requestKey = null;
    createIntent = null;
    retryIntent = null;
    return snapshot();
  }

  function applyJob(job, allowNew = false) {
    if (state.job) {
      if (state.job.id !== job.id && !allowNew) return false;
      if (state.job.id === job.id) {
        if (job.version < state.job.version) return false;
        if (['succeeded', 'cancelled'].includes(state.job.phase) && job.phase !== state.job.phase) return false;
      }
    }
    state.job = copy(job);
    state.items = job.results.map(({ id, name }) => ({ id, name }));
    return true;
  }

  function current(token) { return token.context === context; }

  async function start() {
    if (writer || state.job || state.phase === 'loading'
      || !['idle', 'editing', 'failed', 'uncertain'].includes(state.phase)) return snapshot();
    const invalid = validationError(state.items);
    if (invalid) {
      state.phase = 'failed';
      state.error = invalid;
      return snapshot();
    }
    if (!createIntent) createIntent = { key: operationKey('import'), items: copy(state.items), unknown: false };
    const token = { context, revision: ++revision, kind: 'create' };
    writer = token;
    state.phase = 'submitting';
    state.error = null;
    state.requestKey = createIntent.key;
    try {
      const job = await api.createJob({ key: createIntent.key, items: copy(createIntent.items) });
      if (current(token)) {
        applyJob(job, true);
        state.phase = state.job.phase;
        state.error = null;
        createIntent = null;
      }
    } catch (error) {
      if (current(token)) {
        createIntent.unknown ||= isUnknown(error);
        state.phase = createIntent.unknown ? 'uncertain' : 'failed';
        state.error = errorInfo(error);
        if (createIntent.unknown) state.error.message = '取込みの開始結果を確認できません。同じ取込みを再試行してください。';
      }
    } finally {
      if (writer === token) writer = null;
    }
    return snapshot();
  }

  async function poll() {
    if (!snapshot().canPoll) return snapshot();
    const token = { context, revision, jobId: state.job.id };
    reader = token;
    try {
      const job = await api.getJob(token.jobId);
      if (current(token) && token.revision === revision && job.id === token.jobId) {
        applyJob(job);
        if (retryIntent?.unknown && state.job.generation <= retryIntent.generation) {
          state.phase = 'uncertain';
          state.error = { code: 'RETRY_UNCONFIRMED', message: '再試行の受付はまだ確認できません。同じ失敗項目を再試行できます。' };
        } else {
          retryIntent = null;
          cancelUnknown = false;
          state.phase = state.job.phase;
          state.error = null;
        }
      }
    } catch (error) {
      if (current(token) && token.revision === revision) {
        // 読取りの失敗で、既知の項目結果や進捗を消さない。
        state.error = errorInfo(error, '最新の進捗を確認できませんでした。もう一度更新してください。');
      }
    } finally {
      if (reader === token) reader = null;
    }
    return snapshot();
  }

  async function retryFailed() {
    if (!snapshot().canRetryFailed) return snapshot();
    if (!retryIntent) {
      retryIntent = {
        key: operationKey('retry'), jobId: state.job.id,
        itemIds: state.job.results.filter(row => row.status === 'failed').map(row => row.id),
        generation: state.job.generation, unknown: false,
      };
    }
    const token = { context, revision: ++revision, kind: 'retry' };
    writer = token;
    state.phase = 'submitting';
    state.requestKey = retryIntent.key;
    state.error = null;
    try {
      const job = await api.retryItems({ jobId: retryIntent.jobId, key: retryIntent.key, itemIds: [...retryIntent.itemIds] });
      if (current(token)) {
        applyJob(job);
        state.phase = state.job.phase;
        state.error = null;
        retryIntent = null;
      }
    } catch (error) {
      if (current(token)) {
        retryIntent.unknown ||= isUnknown(error);
        state.phase = retryIntent.unknown ? 'uncertain' : state.job.phase;
        state.error = errorInfo(error);
        if (retryIntent.unknown) state.error.message = '失敗項目の再試行結果を確認できません。進捗の確認、または同じ項目の再試行ができます。';
      }
    } finally {
      if (writer === token) writer = null;
    }
    return snapshot();
  }

  async function cancel() {
    if (!snapshot().canCancel) return snapshot();
    const token = { context, revision: ++revision, kind: 'cancel', jobId: state.job.id };
    writer = token;
    state.phase = 'cancelling';
    state.error = null;
    try {
      const job = await api.cancelJob(token.jobId);
      if (current(token)) {
        applyJob(job);
        state.phase = state.job.phase;
        state.error = null;
        cancelUnknown = false;
      }
    } catch (error) {
      if (current(token)) {
        cancelUnknown = isUnknown(error);
        state.phase = cancelUnknown ? 'uncertain' : state.job.phase;
        state.error = errorInfo(error);
        if (cancelUnknown) state.error.message = '取込みの中止結果を確認できません。進捗を更新して現在の結果を確認してください。';
      }
    } finally {
      if (writer === token) writer = null;
    }
    return snapshot();
  }

  async function resume(jobId) {
    if (writer || state.phase === 'loading' || createIntent?.unknown || retryIntent?.unknown || cancelUnknown) return snapshot();
    const token = { context: ++context, revision: ++revision, jobId };
    reader = token;
    createIntent = null;
    retryIntent = null;
    cancelUnknown = false;
    state.phase = 'loading';
    state.job = null;
    state.items = [];
    state.error = null;
    state.requestKey = null;
    try {
      const job = await api.getJob(jobId);
      if (current(token)) {
        applyJob(job, true);
        state.requestKey = job.key;
        state.phase = job.phase;
      }
    } catch (error) {
      if (current(token)) {
        state.phase = 'failed';
        state.error = errorInfo(error, '取込みを読み戻せませんでした。処理番号を確認してください。');
      }
    } finally {
      if (reader === token) reader = null;
    }
    return snapshot();
  }

  return Object.freeze({ snapshot, setItems, start, poll, retryFailed, cancel, resume });
}
