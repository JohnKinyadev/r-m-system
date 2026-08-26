import api from './index'

export const listProperties = (params) => api.get('/api/properties', { params }).then(r => r.data)
export const getProperty = (id) => api.get(`/api/properties/${id}`).then(r => r.data)
export const createProperty = (data) => api.post('/api/properties', data).then(r => r.data)
export const updateProperty = (id, data) => api.patch(`/api/properties/${id}`, data).then(r => r.data)
export const deleteProperty = (id) => api.delete(`/api/properties/${id}`)
