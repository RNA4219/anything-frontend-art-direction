// Controller 共通処理。DOM・fixture control・タイマーには依存しない。
export const copy = value => JSON.parse(JSON.stringify(value));

let serial = 0;
export function operationKey(prefix) {
  const random = globalThis.crypto?.randomUUID?.()
    ?? `${Date.now().toString(36)}-${(++serial).toString(36)}-${Math.random().toString(36).slice(2)}`;
  return `${prefix}-${random}`;
}

export function errorInfo(error, fallback = '処理を確認できませんでした。もう一度お試しください。') {
  return {
    code: typeof error?.code === 'string' ? error.code : 'UNAVAILABLE',
    message: typeof error?.message === 'string' && error.message ? error.message : fallback,
    ...(error?.fields && typeof error.fields === 'object' ? { fields: copy(error.fields) } : {}),
  };
}

export function isUnknown(error) {
  // 結果の確定をAPIが明示していない輸送エラーも、未実行とは扱わない。
  return error?.outcome !== 'definitive';
}
