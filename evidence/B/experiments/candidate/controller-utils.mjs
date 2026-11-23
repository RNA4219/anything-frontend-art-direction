// 公開APIに渡す入力と、利用者へ返す状態を切り離す。
export const copy = value => JSON.parse(JSON.stringify(value));

let sequence = 0;
export function newKey(prefix) {
  const token = globalThis.crypto?.randomUUID?.()
    ?? `${Date.now().toString(36)}-${(++sequence).toString(36)}-${Math.random().toString(36).slice(2)}`;
  return `${prefix}-${token}`;
}

export function errorInfo(error, fallback) {
  return {
    code: typeof error?.code === 'string' ? error.code : 'UNAVAILABLE',
    message: typeof error?.message === 'string' && error.message ? error.message : fallback,
    ...(error?.fields && typeof error.fields === 'object' ? { fields: copy(error.fields) } : {}),
  };
}

// unknownでないと明示された場合だけ、書込みが確定して失敗したと扱う。
export const outcomeUnknown = error => error?.outcome !== 'definitive';
