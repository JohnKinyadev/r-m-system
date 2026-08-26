import api from './index'

export const listMatingEvents = () => api.get('/api/mating').then(r => r.data)
export const createMatingEvent = (data) => api.post('/api/mating', data).then(r => r.data)
export const listBirths = () => api.get('/api/mating/births').then(r => r.data)
export const logBirth = (data) => api.post('/api/mating/births', data).then(r => r.data)
