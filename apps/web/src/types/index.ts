// User types
export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  roles: string[]
  status: 'active' | 'pending' | 'rejected'
  provider: 'local' | 'entraid'
  created_at: string
}

// Profile types
export type ProfileType = 'admin' | 'agency' | 'company' | 'interim'

export interface AgencyProfile {
  agency_name?: string
  agency_code?: string
  address?: string
  description?: string
}

export interface CompanyProfile {
  company_name?: string
  registration_number?: string
  address?: string
  industry?: string
  company_size?: string
  website?: string
}

export interface InterimProfile {
  skills: string[]
  experience_years?: number
  resume_url?: string
  availability?: string
  bio?: string
  certifications: string[]
}

export interface Profile {
  id: string
  user_id: string
  profile_type: ProfileType
  first_name?: string
  last_name?: string
  phone?: string
  avatar_url?: string
  agency_data?: AgencyProfile
  company_data?: CompanyProfile
  interim_data?: InterimProfile
  completeness: number
  created_at: string
  updated_at: string
}

// Validation types
export type ValidationType = 'company' | 'interim'
export type ValidationStatus = 'pending' | 'approved' | 'rejected'

export interface AccountValidation {
  id: string
  user_id: string
  user_email?: string
  user_name?: string
  validation_type: ValidationType
  status: ValidationStatus
  comment?: string
  reviewed_by?: string
  reviewed_by_email?: string
  reviewed_at?: string
  created_at: string
}

// Notification types
export type NotificationChannel = 'inapp' | 'email' | 'push'
export type NotificationPriority = 'low' | 'normal' | 'high' | 'urgent'

export interface Notification {
  id: string
  user_id: string
  channel: NotificationChannel
  title: string
  body: string
  priority: NotificationPriority
  is_read: boolean
  action_url?: string
  metadata: Record<string, any>
  read_at?: string
  created_at: string
}

// API Response types
export interface LoginResponse {
  access_token: string
  refresh_token?: string
  token_type: string
  expires_in: number
  user: User
}

export interface ValidationListResponse {
  items: AccountValidation[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface NotificationListResponse {
  items: Notification[]
  total: number
  unread_count: number
  page: number
  page_size: number
}

export interface DashboardKPIs {
  validations: {
    pending: number
    approved: number
    rejected: number
    pending_interim: number
    pending_company: number
    recent_rejections_7d: number
  }
  profiles: {
    admin: number
    agency: number
    company: number
    interim: number
    total: number
  }
  active_users: number
}
