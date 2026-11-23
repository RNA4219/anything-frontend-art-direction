import { SimulationError } from '../shared/api.mjs';

// APIのメソッド名・引数・戻り値を変更しないHTTP輸送層。
// controllerへ公開API以外の操作やtest controlを渡さない。
export function createDemoClient(base = new URL('../api/', import.meta.url), fetcher = globalThis.fetch) {
  async function call(group, method, args) {
    let body;
    try {
      const response = await fetcher(new URL(`${group}/${method}`, base), {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ args }),
      });
      body = await response.json();
      if (!body || typeof body.ok !== 'boolean') throw new Error('Invalid response');
    } catch {
      throw new SimulationError('NETWORK', '通信結果を確認できませんでした。', 'unknown');
    }
    if (!body.ok) {
      throw new SimulationError(body.error.code, body.error.message, body.error.outcome, body.error.fields);
    }
    return body.value;
  }
  const make = (group, methods) => Object.freeze(Object.fromEntries(methods.map(method => [method, args => call(group, method, args)])));
  return {
    reservation: make('reservation', ['reserve', 'lookup']),
    inventory: make('inventory', ['createJob', 'getJob', 'retryItems', 'cancelJob']),
  };
}
