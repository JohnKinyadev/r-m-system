import api from './index'

export const getDashboardSummary = () => api.get('/api/reports/dashboard').then(r => r.data)
export const getArrearsReport = () => api.get('/api/reports/arrears').then(r => r.data)
export const getPropertyPerformance = () => api.get('/api/reports/property-performance').then(r => r.data)
