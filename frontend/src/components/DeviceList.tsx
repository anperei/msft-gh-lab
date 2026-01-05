import { Device } from '../types'

interface DeviceListProps {
  devices: Device[]
  onEdit: (device: Device) => void
  onDelete: (id: string) => void
}

export default function DeviceList({ devices, onEdit, onDelete }: DeviceListProps) {
  if (devices.length === 0) {
    return (
      <div className="empty-state">
        <p>No devices found. Add your first device!</p>
      </div>
    )
  }

  return (
    <div className="device-list">
      {devices.map((device) => (
        <div key={device.id} className="device-item">
          <div className="device-info">
            <h3>{device.name}</h3>
            <p>
              {device.assigned_to 
                ? `Assigned to: ${device.assigned_to}` 
                : 'Not assigned'}
            </p>
          </div>
          <div className="device-actions">
            <button 
              className="btn-edit"
              onClick={() => onEdit(device)}
            >
              Edit
            </button>
            <button 
              className="btn-delete"
              onClick={() => onDelete(device.id)}
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
