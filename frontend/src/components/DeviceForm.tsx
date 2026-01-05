import { useState, useEffect } from 'react'
import { Device, DeviceCreate } from '../types'

interface DeviceFormProps {
  device?: Device | null
  onSubmit: (device: DeviceCreate) => void
  onCancel?: () => void
}

export default function DeviceForm({ device, onSubmit, onCancel }: DeviceFormProps) {
  const [name, setName] = useState('')
  const [assignedTo, setAssignedTo] = useState('')

  useEffect(() => {
    if (device) {
      setName(device.name)
      setAssignedTo(device.assigned_to || '')
    } else {
      setName('')
      setAssignedTo('')
    }
  }, [device])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return

    onSubmit({
      name: name.trim(),
      assigned_to: assignedTo.trim() || null,
    })

    if (!device) {
      setName('')
      setAssignedTo('')
    }
  }

  return (
    <form className="device-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="name">Device Name *</label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., Laptop, iPhone, Monitor"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="assignedTo">Assigned To</label>
        <input
          type="text"
          id="assignedTo"
          value={assignedTo}
          onChange={(e) => setAssignedTo(e.target.value)}
          placeholder="e.g., John Doe, Marketing Dept"
        />
      </div>

      <div className="form-actions">
        <button type="submit" className="btn-primary">
          {device ? 'Update Device' : 'Add Device'}
        </button>
        {onCancel && (
          <button type="button" className="btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
