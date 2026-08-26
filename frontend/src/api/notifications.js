import api from './index'

export const listNotifications = () => api.get('/api/notifications').then(r => r.data)
export const markRead = (ids) => api.patch('/api/notifications/mark-read', { ids }).then(r => r.data)
export const markAllRead = () => api.patch('/api/notifications/mark-all-read').then(r => r.data)
