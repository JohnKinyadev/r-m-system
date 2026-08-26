import api from './index'

export const listUsers = () => api.get('/api/users').then(r => r.data)
export const createUser = (data) => api.post('/api/users', data).then(r => r.data)
export const updateUser = (id, data) => api.patch(`/api/users/${id}`, data).then(r => r.data)
export const deleteUser = (id) => api.delete(`/api/users/${id}`)
export const listRoles = () => api.get('/api/roles').then(r => r.data)
export const changePassword = (data) => api.patch('/api/users/me/password', data).then(r => r.data)
