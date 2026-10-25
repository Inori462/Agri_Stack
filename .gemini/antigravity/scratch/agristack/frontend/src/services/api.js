
import axios from 'axios'

const API_URL =
  import.meta.env.VITE_API_URL ||
  'https://agristack-backend-xgdy.onrender.com/api/v1'

const api = axios.create({
  baseURL: API_URL,
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

    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('agristack_refresh')

      if (refresh) {
        try {
          const { data } = await axios.post(
            `${API_URL}/auth/refresh`,
            { refresh_token: refresh }
          )

          localStorage.setItem('agristack_access', data.access_token)

          if (data.refresh_token) {
            localStorage.setItem('agristack_refresh', data.refresh_token)
          }

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
