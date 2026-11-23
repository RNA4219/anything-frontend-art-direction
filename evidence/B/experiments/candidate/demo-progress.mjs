// 通常デモのサーバー進行だけを担当する。製品UIやcontrollerはcontrolを受け取らない。
// 故障注入はここにも置かず、別の自己確認プログラムに置く。
export function createDemoProgress(control) {
  const scheduled = new Set();
  const timers = new Set();
  return {
    observe(job) {
      if (!job || job.phase !== 'running') return;
      job.results.filter(row => row.status === 'pending').forEach((row, index) => {
        const task = `${job.id}:${job.generation}:${row.id}`;
        if (scheduled.has(task)) return;
        scheduled.add(task);
        const timer = setTimeout(() => {
          timers.delete(timer);
          control.completeItem(job.id, row.id, 'succeeded');
        }, 1000 * (index + 1));
        timers.add(timer);
      });
    },
    stop() {
      for (const timer of timers) clearTimeout(timer);
      timers.clear();
    },
  };
}
