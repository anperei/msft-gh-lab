export interface Device {
  id: string
  name: string
  assigned_to: string | null
  created_at: string
  updated_at: string
}

export interface DeviceCreate {
  name: string
  assigned_to: string | null
}
