import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('agristack_access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('agristack_refresh')
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${import.meta.env.VITE_API_URL || '/api/v1'}/auth/refresh`,
            { refresh_token: refresh }
          )
          localStorage.setItem('agristack_access', data.access_token)
          if (data.refresh_token) localStorage.setItem('agristack_refresh', data.refresh_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        } catch {
          localStorage.removeItem('agristack_access')
          localStorage.removeItem('agristack_refresh')
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api
