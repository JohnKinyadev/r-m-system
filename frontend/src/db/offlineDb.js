import { openDB } from 'idb'

const DB_NAME = 'rentmanager-offline'
const DB_VERSION = 1

let _db = null

export async function getDb() {
  if (_db) return _db
  _db = await openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      for (const store of [
        'properties', 'units', 'tenants', 'tenancies',
        'payments', 'maintenance', 'expenses', 'notifications',
      ]) {
        if (!db.objectStoreNames.contains(store)) {
          db.createObjectStore(store, { keyPath: 'id' })
        }
      }
      if (!db.objectStoreNames.contains('pending_mutations')) {
        const s = db.createObjectStore('pending_mutations', { keyPath: 'id', autoIncrement: true })
        s.createIndex('by_created', 'createdAt')
      }
      if (!db.objectStoreNames.contains('sync_meta')) {
        db.createObjectStore('sync_meta')
      }
      if (!db.objectStoreNames.contains('kv')) {
        db.createObjectStore('kv')
      }
    },
  })
  return _db
}

export async function cacheAll(storeName, items) {
  const db = await getDb()
  const tx = db.transaction(storeName, 'readwrite')
  await Promise.all([...items.map(item => tx.store.put(item)), tx.done])
  const meta = db.transaction('sync_meta', 'readwrite')
  await meta.store.put(Date.now(), storeName)
  await meta.done
}

export async function getCached(storeName) {
  const db = await getDb()
  return db.getAll(storeName)
}

export async function upsertCached(storeName, item) {
  const db = await getDb()
  await db.put(storeName, item)
}

export async function deleteCached(storeName, id) {
  const db = await getDb()
  await db.delete(storeName, id)
}

export async function kvGet(key) {
  const db = await getDb()
  return db.get('kv', key)
}

export async function kvSet(key, value) {
  const db = await getDb()
  await db.put('kv', value, key)
}

export async function enqueueMutation(mutation) {
  const db = await getDb()
  await db.add('pending_mutations', { ...mutation, createdAt: Date.now() })
}

export async function getPendingMutations() {
  const db = await getDb()
  return db.getAllFromIndex('pending_mutations', 'by_created')
}

export async function deleteMutation(id) {
  const db = await getDb()
  await db.delete('pending_mutations', id)
}
