import api from './index'

export const listExpenses = () => api.get('/api/expenses').then(r => r.data)
export const createExpense = (data) => api.post('/api/expenses', data).then(r => r.data)
export const updateExpense = (id, data) => api.patch(`/api/expenses/${id}`, data).then(r => r.data)
