import api from './index'

export const login = (email, password) =>
  api.post('/api/auth/login', { email, password }).then(r => r.data)

export const getMe = () =>
  api.get('/api/users/me').then(r => r.data)
