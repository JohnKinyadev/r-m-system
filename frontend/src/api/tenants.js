import api from './index'

export const listTenants = (params) => api.get('/api/tenants', { params }).then(r => r.data)
export const getTenant = (id) => api.get(`/api/tenants/${id}`).then(r => r.data)
export const createTenant = (data) => api.post('/api/tenants', data).then(r => r.data)
export const updateTenant = (id, data) => api.patch(`/api/tenants/${id}`, data).then(r => r.data)
export const deleteTenant = (id) => api.delete(`/api/tenants/${id}`)
