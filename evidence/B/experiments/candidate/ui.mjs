// DOM操作だけを担当する。状態・送信意図はcontroller、通常処理の進行は別モジュール。
export function mount({ reservation, inventory, items }) {
  const element = id => document.getElementById(id);
  const text = (id, value) => { if (element(id).textContent !== value) element(id).textContent = value; };
  const visible = (id, value) => { element(id).hidden = !value; };
  const touched = new Set();
  const importPending = new Set();
  let reservationPending = '';
  let lastResults = '';
  let latestJob = '';
  const storageKey = 'workshop-inventory-job-id';
  const nameInput = element('reservation-name');
  const peopleInput = element('reservation-people');

  function renderReservation() {
    const s = reservation.snapshot();
    const locked = ['submitting', 'uncertain', 'succeeded', 'cancelled'].includes(s.phase) || !!reservationPending;
    for (const [input, field] of [[nameInput, 'name'], [peopleInput, 'people']]) {
      if (input.value !== String(s.draft[field])) input.value = s.draft[field];
      input.disabled = locked;
      const error = s.error?.fields?.[field]
        ?? (touched.has(field) && !input.validity.valid ? input.validationMessage : '');
      text(`${field}-error`, error);
      input.setAttribute('aria-invalid', String(!!error));
    }
    element('reserve-submit').disabled = !s.canSubmit;
    element('reserve-cancel').disabled = !s.canCancel;
    visible('reserve-submit', !['uncertain', 'succeeded', 'cancelled'].includes(s.phase));
    visible('reserve-cancel', !['uncertain', 'submitting', 'succeeded', 'cancelled'].includes(s.phase));
    visible('reserve-retry', ['failed', 'uncertain'].includes(s.phase) && !!s.requestKey);
    visible('reserve-reconcile', s.phase === 'uncertain');
    element('reserve-retry').disabled = !s.canRetry;
    element('reserve-reconcile').disabled = !s.canReconcile;
    visible('reserve-new', ['succeeded', 'cancelled'].includes(s.phase));
    visible('receipt', !!s.receipt);
    if (s.receipt) {
      text('receipt-id', s.receipt.id);
      text('receipt-name', s.receipt.name);
      text('receipt-people', `${s.receipt.people}人`);
    }
    const statuses = {
      idle: '名前と人数を入力してください。', editing: '内容を確認して予約してください。',
      submitting: '予約を送信しています。結果が届くまでお待ちください。',
      succeeded: '予約が確定しました。予約番号を確認できます。',
      failed: '予約を確定できませんでした。下の説明を確認してください。',
      uncertain: '予約結果が確認できていません。', cancelled: '未送信の入力を破棄しました。',
    };
    text('reserve-status', reservationPending === 'reconcile' ? '予約結果を確認しています。' : statuses[s.phase]);
    text('reserve-error', s.error?.message ?? '');
    visible('reserve-error', !!s.error);
  }

  function selectedItems() {
    return items.filter(item => element(`item-${item.id}`).checked).map(item => ({ ...item }));
  }

  function renderImport() {
    const s = inventory.snapshot();
    const locked = ['loading', 'submitting', 'running', 'partial', 'uncertain', 'cancelling'].includes(s.phase)
      || !!s.job && !['succeeded', 'cancelled'].includes(s.job.phase);
    element('import-selection').disabled = locked;
    const selection = new Set(s.items.map(item => item.id));
    for (const item of items) element(`item-${item.id}`).checked = selection.has(item.id);
    element('import-start').disabled = !s.canStart;
    visible('import-start', !s.job && !['loading'].includes(s.phase));
    text('import-start', s.phase === 'uncertain' ? '同じ選択内容で再試行' : '取込みを開始');
    visible('import-cancel', !!s.job && (s.canCancel || s.phase === 'cancelling'));
    element('import-cancel').disabled = !s.canCancel;
    visible('import-poll', !!s.job);
    element('import-poll').disabled = !s.canPoll;
    visible('import-retry', s.canRetryFailed || s.phase === 'submitting' && !!s.job);
    element('import-retry').disabled = !s.canRetryFailed;
    visible('import-cancel-note', !!s.job);
    element('import-resume').disabled = ['submitting', 'cancelling', 'loading'].includes(s.phase);
    element('resume-id').disabled = element('import-resume').disabled;

    const statuses = {
      idle: '取込み対象を選んでください。', editing: `${s.items.length}件が選ばれています。内容を確認してください。`,
      loading: '以前の取込み結果を読み戻しています。',
      submitting: s.job ? '失敗した項目の再試行を受け付けています。' : '取込みの開始を受け付けています。',
      running: '取込み中です。進捗を更新して結果を確認できます。',
      partial: '取込みが終了しました。一部の項目は失敗しています。',
      succeeded: 'すべての項目の取込みが完了しました。',
      failed: '操作を完了できませんでした。下の説明を確認してください。',
      uncertain: '操作の結果を確認できていません。',
      cancelling: '取消しの結果を確認しています。まだ取消しは確定していません。',
      cancelled: '未完了の取込みを取り消しました。取込み済みの結果は保持しています。',
    };
    text('import-status', importPending.has('poll') && s.phase !== 'cancelling' ? '最新の進捗を確認しています。' : statuses[s.phase]);
    text('import-error', s.error?.message ?? '');
    visible('import-error', !!s.error);
    visible('import-job-id', !!s.job);
    visible('progress-region', !!s.job);
    if (s.job) {
      text('import-job-id', `処理番号：${s.job.id}`);
      text('progress-label', `処理済み ${s.progress.processed} / ${s.progress.total}件`);
      element('import-progress').max = Math.max(1, s.progress.total);
      element('import-progress').value = s.progress.processed;
      if (latestJob !== s.job.id) {
        latestJob = s.job.id;
        element('resume-id').value = s.job.id;
        try { sessionStorage.setItem(storageKey, s.job.id); } catch { /* 保存不可でも操作可能 */ }
      }
    }
    const rows = s.job?.results ?? [];
    const signature = JSON.stringify(rows);
    if (signature !== lastResults) {
      lastResults = signature;
      element('import-results').replaceChildren(...rows.map(row => {
        const li = document.createElement('li');
        const name = document.createElement('span'); name.className = 'result-name'; name.textContent = row.name;
        const status = document.createElement('span'); status.className = 'result-state';
        status.textContent = { pending: '処理中', succeeded: '取込み済み', failed: '失敗', cancelled: '取消し済み' }[row.status];
        li.append(name, status);
        if (row.error) { const note = document.createElement('span'); note.className = 'row-error'; note.textContent = row.error; li.append(note); }
        return li;
      }));
    }
  }

  async function runReservation(method) {
    if (reservationPending) return;
    reservationPending = method;
    const pending = reservation[method]();
    renderReservation();
    const timer = setTimeout(() => visible('reserve-slow', true), 12000);
    try { await pending; }
    finally { clearTimeout(timer); reservationPending = ''; visible('reserve-slow', false); renderReservation(); }
  }

  async function runImport(method, argument) {
    if (importPending.has(method)) return;
    importPending.add(method);
    const pending = inventory[method](argument);
    renderImport();
    const timer = setTimeout(() => visible('import-slow', true), 12000);
    try { await pending; }
    finally { clearTimeout(timer); importPending.delete(method); if (!importPending.size) visible('import-slow', false); renderImport(); }
  }

  function editDraft() {
    nameInput.setCustomValidity(nameInput.value.trim() ? '' : '名前を入力してください。');
    reservation.setDraft({ name: nameInput.value, people: peopleInput.value });
    renderReservation();
  }
  for (const [input, key] of [[nameInput, 'name'], [peopleInput, 'people']]) {
    input.addEventListener('input', editDraft);
    input.addEventListener('blur', () => { touched.add(key); renderReservation(); });
    input.addEventListener('invalid', () => { touched.add(key); renderReservation(); });
  }
  element('reservation-form').addEventListener('submit', event => { event.preventDefault(); void runReservation('submit'); });
  element('reserve-retry').addEventListener('click', () => { void runReservation('retry'); });
  element('reserve-reconcile').addEventListener('click', () => { void runReservation('reconcile'); });
  element('reserve-cancel').addEventListener('click', () => { reservation.cancel(); touched.clear(); renderReservation(); element('reserve-new').focus(); });
  element('reserve-new').addEventListener('click', () => {
    reservation.setDraft({ name: '', people: '' }); touched.clear(); nameInput.setCustomValidity(''); renderReservation(); nameInput.focus();
  });

  for (const item of items) {
    const label = document.createElement('label');
    const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.id = `item-${item.id}`;
    checkbox.addEventListener('change', () => { inventory.setItems(selectedItems()); renderImport(); });
    label.append(checkbox, document.createTextNode(item.name)); element('item-options').append(label);
  }
  for (const [id, method] of [['import-start', 'start'], ['import-poll', 'poll'], ['import-retry', 'retryFailed'], ['import-cancel', 'cancel']]) {
    element(id).addEventListener('click', () => { void runImport(method); });
  }
  element('resume-form').addEventListener('submit', event => { event.preventDefault(); void runImport('resume', element('resume-id').value.trim()); });

  inventory.setItems(items.map(item => ({ ...item })));
  renderReservation(); renderImport();
  try {
    const saved = sessionStorage.getItem(storageKey);
    if (saved) { element('resume-id').value = saved; void runImport('resume', saved); }
  } catch { /* 保存領域がない環境では手入力で読み戻す。 */ }
}
