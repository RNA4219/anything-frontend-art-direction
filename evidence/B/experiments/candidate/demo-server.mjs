import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { createReservationHarness, createImportHarness } from '../shared/api.mjs';
import { createDemoProgress } from './demo-progress.mjs';

// メモリ上の共通APIをプロセス内で保持し、画面の再読み込みから独立させる。
// HTTPで公開するのは共通APIの6メソッドだけ。controlとinspectは公開しない。
export function createDemoServer() {
  const reservation = createReservationHarness();
  const inventory = createImportHarness();
  const progress = createDemoProgress(inventory.control);
  const groups = { reservation: reservation.api, inventory: inventory.api };
  const assets = new Map([
    ['/shared/api.mjs', new URL('../shared/api.mjs', import.meta.url)],
    ...['index.html', 'reservation.mjs', 'import-job.mjs', 'controller-utils.mjs', 'ui.mjs', 'demo-client.mjs']
      .map(name => [`/candidate/${name}`, new URL(`./${name}`, import.meta.url)]),
  ]);

  const server = createServer(async (request, response) => {
    const path = new URL(request.url, 'http://127.0.0.1').pathname;
    const json = (status, value) => {
      response.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
      response.end(JSON.stringify(value));
    };
    try {
      if (request.method === 'GET' && path === '/') {
        response.writeHead(302, { Location: '/candidate/index.html' }); response.end(); return;
      }
      if (request.method === 'GET' && assets.has(path)) {
        const content = await readFile(assets.get(path));
        response.writeHead(200, { 'Content-Type': path.endsWith('.html') ? 'text/html; charset=utf-8' : 'text/javascript; charset=utf-8', 'Cache-Control': 'no-store' });
        response.end(content); return;
      }
      const match = /^\/api\/(reservation|inventory)\/([A-Za-z]+)$/.exec(path);
      if (request.method !== 'POST' || !match || !Object.hasOwn(groups[match[1]], match[2])) {
        json(404, { ok: false, error: { code: 'NOT_FOUND', message: '操作が見つかりません。', outcome: 'definitive' } }); return;
      }
      let body = '';
      for await (const chunk of request) {
        body += chunk.toString();
        if (Buffer.byteLength(body) > 16384) {
          json(413, { ok: false, error: { code: 'INVALID_INPUT', message: '入力が長すぎます。', outcome: 'definitive' } }); return;
        }
      }
      let args;
      try { ({ args } = JSON.parse(body)); }
      catch { json(400, { ok: false, error: { code: 'INVALID_INPUT', message: '入力内容を確認してください。', outcome: 'definitive' } }); return; }
      const result = await groups[match[1]][match[2]](args);
      if (match[1] === 'inventory') progress.observe(result);
      json(200, { ok: true, value: result });
    } catch (error) {
      json(200, { ok: false, error: {
        code: error.code ?? 'UNAVAILABLE', message: error.message ?? '処理結果を確認できませんでした。',
        outcome: error.outcome ?? 'unknown', ...(error.fields ? { fields: error.fields } : {}),
      } });
    }
  });
  server.on('close', () => progress.stop());
  return server;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const port = Number(process.env.WORKSHOP_DEMO_PORT || 4173);
  const server = createDemoServer();
  server.listen(port, '127.0.0.1', () => console.log(`画面: http://127.0.0.1:${port}/candidate/index.html`));
}
