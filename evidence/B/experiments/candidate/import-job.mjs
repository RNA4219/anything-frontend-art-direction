import { copy, newKey, errorInfo, outcomeUnknown } from './controller-utils.mjs';

function validateItems(items) {
  if (!Array.isArray(items) || !items.length) return '取り込む項目を選んでください。';
  if (items.some(item => !item || typeof item.id !== 'string' || !item.id.trim()
    || typeof item.name !== 'string' || !item.name.trim())) return '項目にはIDと名前が必要です。';
  if (new Set(items.map(item => item.id)).size !== items.length) return '同じ項目は一度だけ選んでください。';
  return null;
}

export function createImportController(api) {
  const state = { phase: 'idle', items: [], job: null, error: null, requestKey: null };
  let epoch = 0;
  let mutation = 0;
  let writer = null;
  let reader = null;
  let createIntent = null;
  let retryIntent = null;
  let unknown = null; // create / retry / cancel。未解決の副作用は照会失敗で消さない。

  const activeLoad = () => reader?.kind === 'resume';
  const failedIds = () => state.job?.results.filter(row => row.status === 'failed').map(row => row.id) ?? [];

  function snapshot() {
    const available = !writer && !activeLoad();
    return copy({
      ...state,
      progress: state.job?.progress ?? { processed: 0, total: state.items.length },
      canStart: available && !state.job && !validateItems(state.items)
        && ['editing', 'failed', 'uncertain'].includes(state.phase),
      canPoll: available && !reader && !!state.job,
      canRetryFailed: available && state.job?.phase === 'partial' && failedIds().length > 0,
      canCancel: available && state.job?.phase === 'running',
    });
  }

  function setItems(items) {
    if (writer || activeLoad() || state.phase === 'uncertain'
      || (state.job && !['succeeded', 'cancelled'].includes(state.job.phase))) return snapshot();
    epoch++;
    reader = null;
    state.phase = 'editing';
    state.items = copy(items);
    state.job = state.error = state.requestKey = null;
    createIntent = retryIntent = unknown = null;
    return snapshot();
  }

  function acceptJob(job, targetId = null) {
    if (!job || !['running', 'partial', 'succeeded', 'cancelled'].includes(job.phase)
      || !Array.isArray(job.results) || !Number.isInteger(job.version) || (targetId && job.id !== targetId)) {
      const error = new Error('処理結果を確認できませんでした。もう一度確認してください。');
      error.code = 'INVALID_RESPONSE';
      error.outcome = 'unknown';
      throw error;
    }
    const current = state.job;
    if (current?.id === job.id) {
      if (job.version < current.version) return false;
      if (['succeeded', 'cancelled'].includes(current.phase) && job.phase !== current.phase) return false;
    }
    state.job = copy(job);
    state.items = job.results.map(({ id, name }) => ({ id, name }));
    if (retryIntent && job.id === retryIntent.jobId && job.generation > retryIntent.generation) {
      retryIntent = null;
      if (unknown === 'retry') unknown = null;
    }
    if (unknown === 'cancel' && job.phase !== 'running') unknown = null;
    return true;
  }

  function settledPhase() {
    state.phase = unknown ? 'uncertain' : state.job?.phase ?? 'failed';
  }

  async function start() {
    if (writer || activeLoad() || state.job || ['succeeded', 'cancelled'].includes(state.phase)) return snapshot();
    const message = validateItems(state.items);
    if (message) {
      state.phase = 'failed';
      state.error = { code: 'INVALID_ITEMS', message };
      return snapshot();
    }
    if (!createIntent) createIntent = { key: newKey('import'), items: copy(state.items) };
    state.requestKey = createIntent.key;
    state.phase = 'submitting';
    state.error = null;
    const token = writer = { kind: 'create', epoch: ++epoch };
    mutation++;
    try {
      const job = await api.createJob(copy(createIntent));
      if (writer === token) {
        acceptJob(job);
        unknown = null;
        settledPhase();
      }
    } catch (error) {
      if (writer === token) {
        if (outcomeUnknown(error)) unknown = 'create';
        state.phase = unknown ? 'uncertain' : 'failed';
        state.error = errorInfo(error, '取込みを開始できませんでした。');
        if (unknown) state.error.message = '開始結果を確認できません。同じ選択内容で再試行してください。';
      }
    } finally {
      if (writer === token) writer = null;
    }
    return snapshot();
  }

  async function poll() {
    if (!snapshot().canPoll) return snapshot();
    const token = reader = { kind: 'poll', epoch, mutation, jobId: state.job.id };
    try {
      const job = await api.getJob(token.jobId);
      if (token.epoch === epoch && state.job?.id === token.jobId && acceptJob(job, token.jobId)) {
        // 取消要求などの応答待ちは、その書込みの応答が返るまで維持する。
        if (!writer) {
          state.error = null;
          settledPhase();
        }
      }
    } catch (error) {
      if (token.epoch === epoch && token.mutation === mutation && state.job?.id === token.jobId) {
        state.error = errorInfo(error, '進捗を確認できませんでした。最後に確認した結果を表示しています。');
      }
    } finally {
      if (reader === token) reader = null;
    }
    return snapshot();
  }

  async function retryFailed() {
    if (!snapshot().canRetryFailed) return snapshot();
    if (!retryIntent) retryIntent = {
      jobId: state.job.id, key: newKey('retry'), itemIds: failedIds().sort(), generation: state.job.generation,
    };
    const intent = copy(retryIntent);
    const token = writer = { kind: 'retry', epoch, jobId: state.job.id };
    mutation++;
    state.requestKey = intent.key;
    state.phase = 'submitting';
    state.error = null;
    try {
      const job = await api.retryItems({ jobId: intent.jobId, key: intent.key, itemIds: intent.itemIds });
      if (writer === token && token.epoch === epoch) {
        acceptJob(job, intent.jobId);
        if (unknown === 'retry') unknown = null;
        settledPhase();
      }
    } catch (error) {
      if (writer === token && token.epoch === epoch) {
        if (outcomeUnknown(error)) unknown = 'retry';
        state.phase = unknown ? 'uncertain' : 'failed';
        state.error = errorInfo(error, '失敗した項目を再試行できませんでした。');
        if (unknown) state.error.message = '再試行の受付結果が不明です。進捗を確認するか、同じ対象を再試行できます。';
      }
    } finally {
      if (writer === token) writer = null;
    }
    return snapshot();
  }

  async function cancel() {
    if (!snapshot().canCancel) return snapshot();
    const token = writer = { kind: 'cancel', epoch, jobId: state.job.id };
    mutation++;
    state.phase = 'cancelling';
    state.error = null;
    try {
      const job = await api.cancelJob(token.jobId);
      if (writer === token && token.epoch === epoch) {
        acceptJob(job, token.jobId);
        unknown = null;
        settledPhase();
      }
    } catch (error) {
      if (writer === token && token.epoch === epoch) {
        state.error = errorInfo(error, '取消しできませんでした。結果を確認できます。');
        if (state.job && state.job.phase !== 'running') {
          // 取消し応答の前にreadが完了を確認した場合、その実結果を優先する。
          unknown = null;
          settledPhase();
          state.error.message = '取消しの完了は確認できませんでした。表示中の取込み結果は確認済みです。';
        } else {
          if (outcomeUnknown(error)) unknown = 'cancel';
          state.phase = unknown ? 'uncertain' : 'failed';
          if (unknown) state.error.message = '取消し結果を確認できません。進捗を確認してください。';
        }
      }
    } finally {
      if (writer === token) writer = null;
    }
    return snapshot();
  }

  async function resume(jobId) {
    if (writer || (reader?.kind === 'resume' && reader.jobId === jobId)) return snapshot();
    if (typeof jobId !== 'string' || !jobId.trim()) {
      state.error = { code: 'INVALID_JOB_ID', message: '処理番号を入力してください。' };
      if (!state.job) state.phase = 'failed';
      return snapshot();
    }
    const sameJob = state.job?.id === jobId;
    const token = reader = { kind: 'resume', epoch: ++epoch, jobId };
    mutation++;
    state.phase = 'loading';
    state.error = null;
    if (!sameJob) {
      state.job = null;
      state.items = [];
      state.requestKey = null;
      createIntent = retryIntent = unknown = null;
    }
    try {
      const job = await api.getJob(jobId);
      if (token.epoch === epoch) {
        acceptJob(job, jobId);
        state.requestKey ??= job.key;
        settledPhase();
      }
    } catch (error) {
      if (token.epoch === epoch) {
        state.error = errorInfo(error, '取込み結果を読み戻せませんでした。処理番号を確認してください。');
        state.phase = unknown ? 'uncertain' : 'failed';
      }
    } finally {
      if (reader === token) reader = null;
    }
    return snapshot();
  }

  return { snapshot, setItems, start, poll, retryFailed, cancel, resume };
}
