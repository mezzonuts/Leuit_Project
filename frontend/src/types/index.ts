// Core TypeScript Interfaces for LEUIT Frontend

// 1. Database Security State
export interface DatabaseSecurityState {
  is_locked: boolean;
  role: 'OWNER' | 'DEVELOPER' | 'UNAUTHENTICATED';
  last_unlocked_at?: string;
}

// 2. Master Bahan Baku
export interface Ingredient {
  id: number;
  barcode_sku: string | null;
  name: string;
  unit: 'ml' | 'gram' | 'pcs';
  cost_per_unit: number;
  shelf_life_days: number;
  current_stock: number;
  min_stock_threshold: number;
  is_active: boolean;
  lead_time_days?: number;
  created_at?: string;
}

export interface IngredientFormData {
  barcode_sku: string;
  name: string;
  unit: 'ml' | 'gram' | 'pcs';
  cost_per_unit: number;
  shelf_life_days: number;
  current_stock: number;
  min_stock_threshold: number;
  lead_time_days: number;
}

// 3. Rekonsiliasi & Log Sinkronisasi POS
export interface PosSyncResult {
  sync_id: number;
  file_name: string;
  uploaded_at: string;
  total_rows_read: number;
  new_rows_inserted: number;
  duplicate_rows_skipped: number;
  date_range_start: string;
  date_range_end: string;
  reconciled_stock_items: number;
}

export interface PosSyncHistoryItem {
  id: number;
  file_name: string;
  uploaded_at: string;
  total_rows_read: number;
  new_rows_inserted: number;
  duplicate_rows_skipped: number;
  date_range_start: string;
  date_range_end: string;
}

// 4. Pembelian Stok (Cash vs Tempo)
export interface Supplier {
  id: number;
  name: string;
  phone_whatsapp: string | null;
  payment_terms_days: number;
  created_at?: string;
}

export interface SupplierFormData {
  name: string;
  phone_whatsapp: string;
  payment_terms_days: number;
}

export interface InventoryPurchase {
  id: number;
  purchase_date: string;
  ingredient_id: number;
  ingredient_name: string;
  supplier_id: number;
  supplier_name: string;
  quantity: number;
  total_cost: number;
  payment_method: 'CASH' | 'CREDIT';
  payment_status: 'PAID' | 'UNPAID';
  due_date?: string;
  created_at?: string;
}

export interface PurchaseFormData {
  purchase_date: string;
  ingredient_id: number;
  supplier_id: number;
  quantity: number;
  total_cost: number;
  payment_method: 'CASH' | 'CREDIT';
  payment_status: 'PAID' | 'UNPAID';
  due_date?: string;
}

export interface AccountsPayableAlert {
  id: number;
  supplier_name: string;
  total_unpaid: number;
  nearest_due_date: string;
  days_until_due: number;
  purchase_count: number;
}

// 5. Resep / Bill of Materials (BOM)
export interface MenuItem {
  id: number;
  pos_item_id: string | null;
  name: string;
  sale_price: number;
  created_at?: string;
}

export interface RecipeItem {
  id: number;
  menu_item_id: number;
  menu_item_name: string;
  ingredient_id: number;
  ingredient_name: string;
  ingredient_unit: string;
  quantity_required: number;
  cost_per_portion: number;
}

export interface RecipeFormData {
  menu_item_id: number;
  ingredient_id: number;
  quantity_required: number;
}

// 6. Recipe Scaler
export interface RecipeScalerInput {
  menu_item_id: number;
  target_portions: number;
}

export interface RecipeScalerResultItem {
  ingredient_name: string;
  unit: string;
  per_portion: number;
  total_needed: number;
  current_stock: number;
  is_sufficient: boolean;
  deficit: number;
}

export interface RecipeScalerResult {
  menu_name: string;
  target_portions: number;
  items: RecipeScalerResultItem[];
  all_sufficient: boolean;
}

// 7. Dashboard & Analytics
export interface ValuationMetric {
  total_valuation: number;
  total_ingredients: number;
  low_stock_count: number;
  expired_soon_count: number;
}

export interface UsageTrendDataPoint {
  date: string;
  ingredient_id: number;
  ingredient_name: string;
  total_quantity_used: number;
}

export interface StockHealthItem {
  id: number;
  name: string;
  barcode_sku: string | null;
  current_stock: number;
  min_stock_threshold: number;
  unit: string;
  shelf_life_days: number;
  days_until_expiry: number;
  stock_ratio: number;
  status: 'safe' | 'warning' | 'danger';
  cost_per_unit: number;
  valuation: number;
}

export interface CriticalAlertItem {
  id: number;
  name: string;
  type: 'expiry' | 'stock_low';
  message: string;
  severity: 'high' | 'medium';
  ingredient_id?: number;
}

// 8. Forecasting
export interface RestockRecommendation {
  ingredient_id: number;
  ingredient_name: string;
  unit: string;
  current_stock: number;
  predicted_consumption_7d: number;
  recommended_order_qty: number;
  safety_stock: number;
  estimated_cost: number;
  priority: 'high' | 'medium' | 'low';
  supplier_id?: number;
  supplier_name?: string;
  lead_time_days: number;
}

export interface WeatherForecast {
  date: string;
  temperature_min: number;
  temperature_max: number;
  humidity: number;
  rainfall_probability: number;
  weather_description: string;
}

// 9. API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// 10. UI State Types
export type DrawerType = 'ingredient' | 'recipe' | 'purchase' | 'sync' | null;

export interface UIState {
  activeDrawer: DrawerType;
  drawerData: Record<string, any> | null;
  isMobileMenuOpen: boolean;
  licenseGraceDays: number | null;
}