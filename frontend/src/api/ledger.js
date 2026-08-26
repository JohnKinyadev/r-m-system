import api from './index'

export const listLedgerEntries = (params) => api.get('/api/ledger', { params }).then(r => r.data)
export const createLedgerEntry = (data) => api.post('/api/ledger', data).then(r => r.data)
