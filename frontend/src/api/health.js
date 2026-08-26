import api from './index'

export const listHealthLogs = (animalId) => api.get(`/api/health/animal/${animalId}`).then(r => r.data)
export const createHealthLog = (data) => api.post('/api/health', data).then(r => r.data)
export const deleteHealthLog = (id) => api.delete(`/api/health/${id}`)
