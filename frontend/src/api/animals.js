import api from './index'

export const listAnimals = (params) => api.get('/api/animals', { params }).then(r => r.data)
export const getAnimal = (id) => api.get(`/api/animals/${id}`).then(r => r.data)
export const createAnimal = (data) => api.post('/api/animals', data).then(r => r.data)
export const updateAnimal = (id, data) => api.patch(`/api/animals/${id}`, data).then(r => r.data)
export const deleteAnimal = (id) => api.delete(`/api/animals/${id}`)

export const getAnimalWorkers = (id) => api.get(`/api/animals/${id}/workers`).then(r => r.data)
export const setAnimalWorkers = (id, worker_ids) => api.put(`/api/animals/${id}/workers`, { worker_ids }).then(r => r.data)
