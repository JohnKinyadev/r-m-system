import api from './index'

export const listTenancies = () => api.get('/api/tenancies').then(r => r.data)
export const getTenancy = (id) => api.get(`/api/tenancies/${id}`).then(r => r.data)
export const createTenancy = (data) => api.post('/api/tenancies', data).then(r => r.data)
export const updateTenancy = (id, data) => api.patch(`/api/tenancies/${id}`, data).then(r => r.data)
export const moveOutTenancy = (id, data) => api.post(`/api/tenancies/${id}/move-out`, data).then(r => r.data)
