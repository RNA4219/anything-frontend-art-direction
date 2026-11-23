import { copy, errorInfo, isUnknown, operationKey } from './common.mjs';

function validate(draft) {
  const fields = {};
  if (!draft.name.trim()) fields.name = '名前を入力してください。';
  const people = typeof draft.people === 'string' && !draft.people.trim() ? NaN : Number(draft.people);
  if (!Number.isInteger(people) || people < 1 || people > 8) {
    fields.people = '参加人数は1〜8の整数で入力してください。';
  }
  return {
    valid: Object.keys(fields).length === 0,
    normalized: { name: draft.name.trim(), people },
    error: { code: 'VALIDATION', message: '入力内容を確認してください。', fields },
  };
}

export function createReservationController(api) {
  const state = {
    phase: 'idle', draft: { name: '', people: '' }, receipt: null, error: null, requestKey: null,
  };
  let intent = null;
  let busy = false;

  function snapshot() {
    const valid = validate(state.draft).valid;
    const editable = ['idle', 'editing', 'failed'].includes(state.phase) && !intent;
    return copy({
      ...state,
      canSubmit: !busy && editable && valid,
      canRetry: !busy && !!intent && ['failed', 'uncertain'].includes(state.phase),
      canReconcile: !busy && !!intent && state.phase === 'uncertain',
      canCancel: !busy && !intent?.unknown && ['editing', 'failed'].includes(state.phase),
    });
  }

  function setDraft(patch) {
    if (busy || ['submitting', 'uncertain'].includes(state.phase)) return snapshot();
    state.draft = { ...state.draft, ...patch };
    state.phase = 'editing';
    state.receipt = null;
    state.error = null;
    state.requestKey = null;
    intent = null;
    return snapshot();
  }

  async function send() {
    busy = true;
    state.phase = 'submitting';
    state.error = null;
    try {
      const receipt = await api.reserve({ key: intent.key, draft: copy(intent.draft) });
      state.receipt = copy(receipt);
      state.phase = 'succeeded';
      state.error = null;
      intent.unknown = false;
    } catch (error) {
      intent.unknown ||= isUnknown(error);
      state.phase = intent.unknown ? 'uncertain' : 'failed';
      state.error = errorInfo(error);
      if (intent.unknown) {
        state.error.message = '予約結果を確認できません。結果の確認、または同じ予約の再試行を行ってください。';
      }
    } finally {
      busy = false;
    }
    return snapshot();
  }

  async function submit() {
    if (busy || intent || !['idle', 'editing', 'failed'].includes(state.phase)) return snapshot();
    const validation = validate(state.draft);
    if (!validation.valid) {
      state.phase = 'failed';
      state.error = validation.error;
      return snapshot();
    }
    intent = { key: operationKey('reservation'), draft: validation.normalized, unknown: false };
    state.requestKey = intent.key;
    return send();
  }

  async function retry() {
    if (!snapshot().canRetry) return snapshot();
    return send();
  }

  async function reconcile() {
    if (!snapshot().canReconcile) return snapshot();
    busy = true;
    state.error = null;
    try {
      const result = await api.lookup(intent.key);
      if (result.found && result.receipt) {
        state.receipt = copy(result.receipt);
        state.phase = 'succeeded';
        intent.unknown = false;
      } else {
        state.phase = 'uncertain';
        state.error = {
          code: 'NOT_YET_CONFIRMED',
          message: '予約はまだ確認できません。同じ予約を再試行できます。最初の送信が未実行とは断定できません。',
        };
      }
    } catch (error) {
      state.phase = 'uncertain';
      state.error = errorInfo(error, '予約結果の確認に失敗しました。もう一度確認してください。');
    } finally {
      busy = false;
    }
    return snapshot();
  }

  function cancel() {
    if (!snapshot().canCancel) return snapshot();
    state.phase = 'cancelled';
    state.draft = { name: '', people: '' };
    state.receipt = null;
    state.error = null;
    state.requestKey = null;
    intent = null;
    return snapshot();
  }

  return Object.freeze({ snapshot, setDraft, submit, retry, reconcile, cancel });
}
