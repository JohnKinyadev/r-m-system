import api from './index'

export const listMaintenanceRequests = (params) => api.get('/api/maintenance', { params }).then(r => r.data)
export const createMaintenanceRequest = (data) => api.post('/api/maintenance', data).then(r => r.data)
export const updateMaintenanceRequest = (id, data) => api.patch(`/api/maintenance/${id}`, data).then(r => r.data)
