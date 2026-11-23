import { copy, newKey, errorInfo, outcomeUnknown } from './controller-utils.mjs';

function validate(draft) {
  const fields = {};
  if (typeof draft.name !== 'string' || !draft.name.trim()) fields.name = '名前を入力してください。';
  const people = typeof draft.people === 'string' && !draft.people.trim() ? NaN : Number(draft.people);
  if (!Number.isInteger(people) || people < 1 || people > 8) {
    fields.people = '参加人数は1〜8の整数で入力してください。';
  }
  return Object.keys(fields).length
    ? { error: { code: 'VALIDATION', message: '入力内容を確認してください。', fields } }
    : { draft: { name: draft.name.trim(), people } };
}

export function createReservationController(api) {
  const state = {
    phase: 'idle', draft: { name: '', people: '' }, receipt: null, error: null, requestKey: null,
  };
  let intent = null;
  let busy = false;
  // 後続の拒否やnot-foundで、以前の不明な書込みを「未実行」に変えない。
  let unresolved = false;

  function snapshot() {
    const valid = !validate(state.draft).error;
    return copy({
      ...state,
      canSubmit: !busy && valid && ['idle', 'editing', 'failed'].includes(state.phase) && !intent,
      canRetry: !busy && !!intent && ['failed', 'uncertain'].includes(state.phase),
      canReconcile: !busy && state.phase === 'uncertain' && !!state.requestKey,
      canCancel: !busy && !unresolved && ['editing', 'failed'].includes(state.phase),
    });
  }

  function setDraft(patch) {
    if (busy || ['submitting', 'uncertain'].includes(state.phase)) return snapshot();
    state.draft = {
      name: Object.hasOwn(patch, 'name') ? patch.name : state.draft.name,
      people: Object.hasOwn(patch, 'people') ? patch.people : state.draft.people,
    };
    state.phase = 'editing';
    state.error = state.receipt = state.requestKey = null;
    intent = null;
    unresolved = false;
    return snapshot();
  }

  function confirm(receipt) {
    if (!receipt || receipt.status !== 'confirmed' || receipt.key !== state.requestKey || !receipt.id) {
      const error = new Error('予約結果を確認できませんでした。同じ内容で結果を確認してください。');
      error.code = 'INVALID_RESPONSE';
      error.outcome = 'unknown';
      throw error;
    }
    state.receipt = copy(receipt);
    state.phase = 'succeeded';
    state.error = null;
    unresolved = false;
  }

  async function send() {
    busy = true;
    state.phase = 'submitting';
    state.error = null;
    try {
      confirm(await api.reserve(copy(intent)));
    } catch (error) {
      unresolved ||= outcomeUnknown(error);
      state.phase = unresolved ? 'uncertain' : 'failed';
      state.error = errorInfo(error, '送信できませんでした。入力を保持しています。');
      if (unresolved) state.error.message = '予約結果がまだ確認できません。結果を照会するか、同じ内容で再試行してください。';
    } finally {
      busy = false;
    }
    return snapshot();
  }

  async function submit() {
    if (busy || ['submitting', 'uncertain', 'succeeded', 'cancelled'].includes(state.phase) || intent) return snapshot();
    const checked = validate(state.draft);
    if (checked.error) {
      state.phase = 'failed';
      state.error = checked.error;
      return snapshot();
    }
    state.requestKey = newKey('reservation');
    intent = { key: state.requestKey, draft: checked.draft };
    return send();
  }

  async function retry() {
    if (!snapshot().canRetry) return snapshot();
    return send();
  }

  async function reconcile() {
    if (!snapshot().canReconcile) return snapshot();
    busy = true;
    try {
      const found = await api.lookup(state.requestKey);
      if (found.found && found.receipt) confirm(found.receipt);
      else {
        state.phase = 'uncertain';
        state.error = { code: 'NOT_CONFIRMED', message: '予約はまだ見つかりません。未実行とは確定していません。同じ内容で再試行できます。' };
      }
    } catch (error) {
      state.phase = 'uncertain';
      state.error = errorInfo(error, '結果を照会できませんでした。');
      state.error.message = '結果を照会できませんでした。予約結果は不明のままです。もう一度確認できます。';
    } finally {
      busy = false;
    }
    return snapshot();
  }

  function cancel() {
    if (!snapshot().canCancel) return snapshot();
    state.phase = 'cancelled';
    state.draft = { name: '', people: '' };
    state.receipt = state.error = state.requestKey = null;
    intent = null;
    return snapshot();
  }

  return { snapshot, setDraft, submit, retry, reconcile, cancel };
}
