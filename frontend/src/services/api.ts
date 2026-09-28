import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    const passkey = localStorage.getItem('leuit_passkey')
    if (passkey) {
      config.headers['X-Passkey'] = passkey
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('leuit_passkey')
      window.location.href = '/unlock'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  unlock: (passkey: string, isDeveloper = false) =>
    api.post('/auth/unlock', { passkey, is_developer: isDeveloper }),
  status: () => api.get('/auth/status'),
}

// Inventory API
export const inventoryApi = {
  list: (params?: { skip?: number; limit?: number; search?: string; active_only?: boolean }) =>
    api.get('/inventory', { params }),
  get: (id: number) => api.get(`/inventory/${id}`),
  create: (data: any) => api.post('/inventory', data),
  update: (id: number, data: any) => api.put(`/inventory/${id}`, data),
  delete: (id: number) => api.delete(`/inventory/${id}`),
  stockOpname: (id: number, quantity: number) => api.post(`/inventory/${id}/stock-opname`, { quantity }),
  valuation: () => api.get('/valuation'),
  exportValuation: () => api.get('/valuation/export-csv', { responseType: 'blob' }),
}

// Recipe/BOM API
export const bomApi = {
  listMenus: () => api.get('/bom/menus'),
  getMenu: (id: number) => api.get(`/bom/menus/${id}`),
  createMenu: (data: any) => api.post('/bom/menus', data),
  updateMenu: (id: number, data: any) => api.put(`/bom/menus/${id}`, data),
  deleteMenu: (id: number) => api.delete(`/bom/menus/${id}`),
  listRecipes: (menuId: number) => api.get(`/bom/menus/${menuId}/recipes`),
  createRecipe: (data: any) => api.post('/bom/recipes', data),
  updateRecipe: (id: number, data: any) => api.put(`/bom/recipes/${id}`, data),
  deleteRecipe: (id: number) => api.delete(`/bom/recipes/${id}`),
  scaler: (data: any) => api.post('/bom/scaler', data),
}

// Purchases API
export const purchasesApi = {
  list: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/purchases', { params }),
  create: (data: any) => api.post('/purchases', data),
  pay: (id: number) => api.post(`/purchases/${id}/pay`),
  payables: () => api.get('/purchases/payables'),
  restockSheet: () => api.get('/purchases/restock-sheet'),
  suppliers: {
    list: () => api.get('/purchases/suppliers'),
    create: (data: any) => api.post('/purchases/suppliers', data),
    update: (id: number, data: any) => api.put(`/purchases/suppliers/${id}`, data),
    delete: (id: number) => api.delete(`/purchases/suppliers/${id}`),
  },
}

// POS Sync API
export const syncApi = {
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/sync/pos-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  history: (params?: { skip?: number; limit?: number }) =>
    api.get('/sync/history', { params }),
  getResult: (id: number) => api.get(`/sync/history/${id}`),
}

// Forecast API
export const forecastApi = {
  restockSheet: () => api.get('/forecast/restock-sheet'),
  weather: (adm4?: string) => api.get('/forecast/weather', { params: { adm4 } }),
}