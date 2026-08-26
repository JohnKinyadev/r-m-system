import api from './index'

export const getWorkerPermissions = (userId) =>
  api.get(`/api/users/${userId}/permissions`).then(r => r.data)

export const setWorkerPermissions = (userId, modules) =>
  api.put(`/api/users/${userId}/permissions`, { modules }).then(r => r.data)
