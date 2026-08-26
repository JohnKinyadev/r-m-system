import api from './index'

export const listLivestockTypes = () => api.get('/api/livestock-types').then(r => r.data)
export const getLivestockType = (id) => api.get(`/api/livestock-types/${id}`).then(r => r.data)
export const createLivestockType = (data) => api.post('/api/livestock-types', data).then(r => r.data)
export const updateLivestockType = (id, data) => api.patch(`/api/livestock-types/${id}`, data).then(r => r.data)
export const deleteLivestockType = (id) => api.delete(`/api/livestock-types/${id}`)
