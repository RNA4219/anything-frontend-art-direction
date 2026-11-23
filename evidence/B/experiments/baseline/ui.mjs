import { createReservationController } from './reservation.mjs';
import { createImportController } from './import-job.mjs';
import { createDemoSession } from './demo-runtime.mjs';

export async function mount({ reservationHarness, importHarness, inventoryItems }) {
  const $ = id => document.getElementById(id);
  let storage = null;
  try { storage = window.localStorage; } catch { /* 保存なしでも現在の操作は利用できる。 */ }
  const demo = await createDemoSession(reservationHarness, importHarness, storage);
  // controllerへ渡すのは共通APIの公開メソッドだけ。
  const reservation = createReservationController(reservationHarness.api);
  const importer = createImportController(importHarness.api);
  const touched = new Set();
  let reservationAction = null;
  const importActions = new Map();
  const checkboxes = [...$('import-selection').querySelectorAll('input')];

  const showText = (element, text) => {
    element.textContent = text ?? '';
    element.hidden = !text;
  };

  function renderReservation() {
    const s = reservation.snapshot();
    const locked = ['submitting', 'uncertain', 'succeeded'].includes(s.phase);
    const inputName = $('reservation-name');
    const inputPeople = $('reservation-people');
    if (inputName.value !== s.draft.name) inputName.value = s.draft.name;
    if (inputPeople.value !== String(s.draft.people)) inputPeople.value = s.draft.people;
    inputName.readOnly = locked;
    inputPeople.readOnly = locked;
    $('reservation-form').setAttribute('aria-busy', String(s.phase === 'submitting'));
    const invalidName = touched.has('name') && !s.draft.name.trim();
    const n = Number(s.draft.people);
    const invalidPeople = touched.has('people') && (String(s.draft.people).trim() === '' || !Number.isInteger(n) || n < 1 || n > 8);
    const nameMessage = s.error?.fields?.name ?? (invalidName ? '名前を入力してください。' : '');
    const peopleMessage = s.error?.fields?.people ?? (invalidPeople ? '参加人数は1〜8の整数で入力してください。' : '');
    showText($('name-error'), nameMessage);
    showText($('people-error'), peopleMessage);
    inputName.setAttribute('aria-invalid', String(!!nameMessage));
    inputPeople.setAttribute('aria-invalid', String(!!peopleMessage));

    const recovering = ['retry', 'reconcile'].includes(reservationAction)
      || (s.requestKey && ['failed', 'uncertain'].includes(s.phase));
    $('reservation-submit').disabled = !s.canSubmit;
    $('reservation-submit').hidden = !!s.receipt || !!recovering;
    $('reservation-submit').textContent = s.phase === 'submitting' ? '予約を送信しています…' : '予約を確定する';
    $('reservation-cancel').disabled = !s.canCancel;
    $('reservation-cancel').hidden = s.phase === 'succeeded';
    $('reservation-recovery').hidden = !recovering;
    $('reservation-retry').disabled = !s.canRetry;
    $('reservation-retry').textContent = reservationAction === 'retry' ? '同じ予約を送信しています…' : '同じ予約を再試行する';
    $('reservation-reconcile').hidden = s.phase !== 'uncertain' && reservationAction !== 'reconcile';
    $('reservation-reconcile').disabled = !s.canReconcile;
    $('reservation-reconcile').textContent = reservationAction === 'reconcile' ? '予約結果を確認しています…' : '予約結果を確認する';
    const messages = {
      idle: '名前と人数を入力してください。',
      editing: s.canSubmit ? '入力内容を確認して予約を確定してください。' : '名前と1〜8人の参加人数を入力してください。',
      submitting: '予約を送信しています。結果が届くまでお待ちください。',
      succeeded: '予約が確定しました。予約番号をご確認ください。',
      failed: s.requestKey ? '予約を確定できませんでした。入力は保持しています。' : '入力内容を確認してください。',
      uncertain: '予約結果を確認できていません。予約が完了している可能性があります。',
      cancelled: '未確定の入力を破棄しました。新しい内容を入力できます。',
    };
    $('reservation-status').textContent = reservationAction === 'reconcile'
      ? '予約結果を確認しています…' : messages[s.phase];
    showText($('reservation-error'), s.error ? `確認が必要です：${s.error.message}` : '');
    $('reservation-close-note').hidden = !['submitting', 'uncertain'].includes(s.phase);
    $('reservation-receipt').hidden = !s.receipt;
    if (s.receipt) {
      $('receipt-id').textContent = s.receipt.id;
      $('receipt-name').textContent = s.receipt.name;
      $('receipt-people').textContent = `${s.receipt.people}人`;
    }
    $('reservation-new').hidden = s.phase !== 'succeeded';
  }

  function renderImport() {
    const s = importer.snapshot();
    const locked = !!s.job || ['loading', 'submitting', 'uncertain', 'cancelling'].includes(s.phase);
    $('import-selection').disabled = locked;
    for (const checkbox of checkboxes) checkbox.checked = s.items.some(item => item.id === checkbox.value);
    $('selection-help').textContent = s.items.length ? `${s.items.length}件を選択しています。` : '取込み対象を1件以上選んでください。';
    $('import-start').hidden = !!s.job || s.phase === 'loading';
    $('import-start').disabled = !s.canStart;
    $('import-start').textContent = s.phase === 'submitting' ? '取込みを開始しています…'
      : s.phase === 'uncertain' ? '同じ取込みを再試行する'
      : s.phase === 'failed' ? '取込みを再試行する' : '取込みを開始する';
    $('import-poll').hidden = !s.job;
    $('import-poll').disabled = !s.canPoll;
    $('import-poll').textContent = importActions.has('poll') ? '進捗を確認しています…' : '進捗を更新する';
    $('import-retry').hidden = !s.job || (s.job.phase !== 'partial' && !importActions.has('retry'));
    $('import-retry').disabled = !s.canRetryFailed;
    $('import-retry').textContent = importActions.has('retry') ? '失敗した項目を再送信しています…' : '失敗した項目を再試行する';
    $('import-cancel').hidden = !s.job || (!['running', 'cancelling', 'uncertain'].includes(s.phase));
    $('import-cancel').disabled = !s.canCancel;
    $('import-cancel').textContent = s.phase === 'cancelling' ? '中止の結果を確認しています…' : '取込みを中止する';
    $('resume-button').disabled = !($('resume-id').value.trim()) || ['loading', 'submitting', 'cancelling', 'uncertain'].includes(s.phase);
    $('resume-id').disabled = ['loading', 'submitting', 'cancelling', 'uncertain'].includes(s.phase);

    const messages = {
      idle: '取込み対象を確認してください。',
      editing: s.items.length ? '選んだ項目を確認して取込みを開始してください。' : '取込み対象を選んでください。',
      loading: '前の取込み結果を読み戻しています…',
      submitting: s.job ? '失敗した項目の再試行を送信しています…' : '取込みの開始を受け付けています…',
      running: '取込みを処理しています。進捗を更新して結果を確認できます。',
      partial: '取込みが終わりました。一部の項目が失敗しています。',
      succeeded: 'すべての項目の取込みが完了しました。',
      failed: '取込みを開始、または読み戻すことができませんでした。',
      uncertain: '操作の結果を確認できていません。下の案内に沿って確認してください。',
      cancelling: '取込みの中止を要求しています。結果が届くまでお待ちください。',
      cancelled: '取込みの中止を確認しました。中止前に完了した項目は保持されています。',
    };
    $('import-status').textContent = importActions.has('poll') && s.phase !== 'cancelling'
      ? '最新の進捗を確認しています。表示中の結果は保持しています。' : messages[s.phase];
    showText($('import-error'), s.error ? `確認が必要です：${s.error.message}` : '');
    $('import-progress').hidden = !s.job;
    if (s.job) {
      const succeeded = s.job.results.filter(row => row.status === 'succeeded').length;
      const failed = s.job.results.filter(row => row.status === 'failed').length;
      const cancelled = s.job.results.filter(row => row.status === 'cancelled').length;
      $('import-id').textContent = `処理番号：${s.job.id}`;
      $('import-bar').max = s.progress.total;
      $('import-bar').value = s.progress.processed;
      $('import-count').textContent = `${s.progress.processed} / ${s.progress.total} 件を処理済み（成功 ${succeeded}件・失敗 ${failed}件${cancelled ? `・中止 ${cancelled}件` : ''}）`;
      const labels = { pending: '処理待ち', succeeded: '成功', failed: '失敗', cancelled: '中止' };
      const fragment = document.createDocumentFragment();
      for (const row of s.job.results) {
        const tr = document.createElement('tr');
        const name = document.createElement('th');
        name.scope = 'row';
        name.textContent = row.name;
        const result = document.createElement('td');
        result.textContent = labels[row.status];
        if (row.error) {
          const detail = document.createElement('small');
          detail.textContent = row.error;
          result.append(detail);
        }
        tr.append(name, result);
        fragment.append(tr);
      }
      $('import-results').replaceChildren(fragment);
    }
    $('import-new').hidden = !['succeeded', 'cancelled'].includes(s.phase);
    $('storage-note').hidden = demo.storageAvailable;
  }

  async function runReservation(action, operation) {
    if (reservationAction) return;
    reservationAction = action;
    const pending = operation();
    renderReservation();
    try { await pending; }
    finally {
      reservationAction = null;
      demo.afterAction();
      renderReservation();
      if (reservation.snapshot().error?.fields?.name) $('reservation-name').focus();
      else if (reservation.snapshot().error?.fields?.people) $('reservation-people').focus();
      else $('reservation-status').focus();
    }
  }

  async function runImport(action, operation) {
    if (importActions.has(action)) return;
    const token = Symbol(action);
    importActions.set(action, token);
    const pending = operation();
    renderImport();
    try { await pending; }
    finally {
      if (importActions.get(action) === token) importActions.delete(action);
      demo.afterAction(importer.snapshot().job);
      renderImport();
      if (action !== 'poll') $('import-status').focus();
    }
  }

  function safeAction(operation) {
    // UIのイベント境界でも拒否を処理し、操作後に表示可能な説明を残す。
    Promise.resolve().then(operation).catch(() => {
      $('startup').hidden = false;
      $('startup').textContent = '操作を表示に反映できませんでした。現在の結果を確認してください。';
    });
  }

  for (const [id, key] of [['reservation-name', 'name'], ['reservation-people', 'people']]) {
    $(id).addEventListener('input', () => {
      touched.add(key);
      reservation.setDraft({ [key]: $(id).value });
      renderReservation();
    });
    $(id).addEventListener('blur', () => { touched.add(key); renderReservation(); });
  }
  $('reservation-form').addEventListener('submit', event => {
    event.preventDefault();
    touched.add('name'); touched.add('people');
    safeAction(() => runReservation('submit', () => reservation.submit()));
  });
  $('reservation-retry').addEventListener('click', () => safeAction(() => runReservation('retry', () => reservation.retry())));
  $('reservation-reconcile').addEventListener('click', () => safeAction(() => runReservation('reconcile', () => reservation.reconcile())));
  $('reservation-cancel').addEventListener('click', () => {
    reservation.cancel(); touched.clear(); renderReservation(); $('reservation-status').focus();
  });
  $('reservation-new').addEventListener('click', () => {
    reservation.setDraft({ name: '', people: '' }); touched.clear(); renderReservation(); $('reservation-name').focus();
  });
  for (const checkbox of checkboxes) checkbox.addEventListener('change', () => {
    importer.setItems(inventoryItems.filter(item => checkboxes.some(box => box.checked && box.value === item.id)));
    renderImport();
  });
  $('import-start').addEventListener('click', () => safeAction(() => runImport('start', () => importer.start())));
  $('import-poll').addEventListener('click', () => safeAction(() => runImport('poll', () => importer.poll())));
  $('import-retry').addEventListener('click', () => safeAction(() => runImport('retry', () => importer.retryFailed())));
  $('import-cancel').addEventListener('click', () => safeAction(() => runImport('cancel', () => importer.cancel())));
  $('import-new').addEventListener('click', () => {
    importer.setItems(inventoryItems); renderImport(); checkboxes[0].focus();
  });
  $('resume-id').addEventListener('input', renderImport);
  $('resume-form').addEventListener('submit', event => {
    event.preventDefault();
    const jobId = $('resume-id').value.trim();
    if (jobId) safeAction(() => runImport('resume', () => importer.resume(jobId)));
  });
  window.addEventListener('pagehide', () => demo.dispose());

  importer.setItems(inventoryItems);
  renderReservation();
  renderImport();
  $('startup').hidden = true;
  if (demo.lastJobId) {
    $('resume-id').value = demo.lastJobId;
    await runImport('resume', () => importer.resume(demo.lastJobId));
  }
}
