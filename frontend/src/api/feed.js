import api from './index'

export const listFeedTypes = () => api.get('/api/feed/types').then(r => r.data)
export const createFeedType = (data) => api.post('/api/feed/types', data).then(r => r.data)
export const updateFeedType = (id, data) => api.patch(`/api/feed/types/${id}`, data).then(r => r.data)

export const logStockArrival = (data) => api.post('/api/feed/stock-arrivals', data).then(r => r.data)
export const listStockArrivals = () => api.get('/api/feed/stock-arrivals').then(r => r.data)

export const logFeedingSession = (data) => api.post('/api/feed/logs', data).then(r => r.data)
export const listFeedLogs = () => api.get('/api/feed/logs').then(r => r.data)
