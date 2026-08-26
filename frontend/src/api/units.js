import api from './index'

export const listUnits = (params) => api.get('/api/units', { params }).then(r => r.data)
export const getUnit = (id) => api.get(`/api/units/${id}`).then(r => r.data)
export const createUnit = (data) => api.post('/api/units', data).then(r => r.data)
export const updateUnit = (id, data) => api.patch(`/api/units/${id}`, data).then(r => r.data)
export const deleteUnit = (id) => api.delete(`/api/units/${id}`)
