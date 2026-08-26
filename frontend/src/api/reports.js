import api from './index'

export const getDashboardSummary = () => api.get('/api/reports/dashboard').then(r => r.data)
export const getHerdHealth = () => api.get('/api/reports/herd-health').then(r => r.data)
export const getFeedConsumption = () => api.get('/api/reports/feed-consumption').then(r => r.data)
export const getBirthMortality = () => api.get('/api/reports/birth-mortality').then(r => r.data)
