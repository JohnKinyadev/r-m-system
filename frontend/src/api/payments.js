import api from './index'

export const listPayments = () => api.get('/api/payments').then(r => r.data)
export const createPayment = (data) => api.post('/api/payments', data).then(r => r.data)
