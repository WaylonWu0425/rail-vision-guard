const STORE = 'cases';

async function withStore(mode, operation) {
  const db = await new Promise((resolve, reject) => {
    const request = indexedDB.open('rail-vision-coupler-review', 1);
    request.onupgradeneeded = () => {
      request.result.createObjectStore(STORE, { keyPath: ['owner', 'id'] });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
  try {
    return await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, mode);
      let result, failure;
      tx.oncomplete = () => resolve(result);
      tx.onabort = () => reject(failure || tx.error || new Error('本地归档事务中断。'));
      operation(tx.objectStore(STORE), value => { result = value; }, error => {
        failure = error;
        tx.abort();
      });
    });
  } finally {
    db.close();
  }
}

export function listCases(owner) {
  return withStore('readonly', (store, done) => {
    const range = IDBKeyRange.bound([owner, ''], [owner, '\uffff']);
    const request = store.getAll(range);
    request.onsuccess = () => done(request.result.sort((a, b) => b.createdAt.localeCompare(a.createdAt)));
  });
}

export function archiveCase(item) {
  return withStore('readwrite', (store, done) => {
    const request = store.add(JSON.parse(JSON.stringify(item)));
    request.onsuccess = () => done(item);
  });
}

export function appendReview(owner, id, expectedVersion, review) {
  return withStore('readwrite', (store, done, abort) => {
    const read = store.get([owner, id]);
    read.onsuccess = () => {
      const item = read.result;
      if (!item || item.reviews.length !== expectedVersion) {
        abort(new Error('该记录已有更新，请刷新归档后查看最新版本。'));
        return;
      }
      item.reviews.push(review);
      const written = store.put(item);
      written.onsuccess = () => done(item);
    };
  });
}

export function downloadJson(data, filename) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
