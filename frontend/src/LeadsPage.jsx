import { useState, useEffect, useCallback } from 'react'
import { apiFetch, authFetch, clearAuth } from './api'

const STATUSES = ['new', 'contacted', 'qualified', 'lost']

const STATUS_COLORS = {
  new: '#3b82f6',
  contacted: '#f59e0b',
  qualified: '#10b981',
  lost: '#ef4444',
}

function StatusBadge({ status }) {
  return (
    <span
      style={{
        background: STATUS_COLORS[status] || '#6b7280',
        color: '#fff',
        padding: '2px 10px',
        borderRadius: 12,
        fontSize: 12,
        fontWeight: 600,
        textTransform: 'capitalize',
      }}
    >
      {status}
    </span>
  )
}

const EMPTY_FORM = { name: '', email: '', phone: '', budget: '', notes: '' }

export default function LeadsPage({ member, onLogout }) {
  const [leads, setLeads] = useState([])
  const [statusFilter, setStatusFilter] = useState('')
  const [form, setForm] = useState(EMPTY_FORM)
  const [formError, setFormError] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const fetchLeads = useCallback(async () => {
    setLoading(true)
    try {
      const url = statusFilter ? `/api/leads?status=${statusFilter}` : '/api/leads'
      const res = await apiFetch(url)
      if (!res.ok) throw new Error('Failed to fetch leads')
      setLeads(await res.json())
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => {
    fetchLeads()
  }, [fetchLeads])

  async function handleSubmit(e) {
    e.preventDefault()
    setFormError('')
    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim() || null,
      budget: form.budget ? parseFloat(form.budget) : null,
      notes: form.notes.trim() || null,
    }
    setSubmitting(true)
    try {
      const res = await apiFetch('/api/leads', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      const data = await res.json()
      if (!res.ok) { setFormError(data.error || 'Something went wrong'); return }
      setForm(EMPTY_FORM)
      fetchLeads()
    } catch {
      setFormError('Network error')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleStatusChange(lead, newStatus) {
    try {
      const res = await apiFetch(`/api/leads/${lead.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      })
      if (!res.ok) return
      setLeads((prev) => prev.map((l) => (l.id === lead.id ? { ...l, status: newStatus } : l)))
    } catch (err) { console.error(err) }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this lead?')) return
    try {
      const res = await apiFetch(`/api/leads/${id}`, { method: 'DELETE' })
      if (res.ok || res.status === 204) setLeads((prev) => prev.filter((l) => l.id !== id))
    } catch (err) { console.error(err) }
  }

  async function handleLogout() {
    try {
      await authFetch('/api/members/logout', { method: 'DELETE' })
    } catch { /* best-effort */ }
    clearAuth()
    onLogout()
  }

  return (
    <div className="container">
      <header className="page-header">
        <h1>BaliHouses Lead Tracker</h1>
        <div className="header-right">
          <span className="member-name">Hi, {member?.name}</span>
          <button className="btn btn-outline" onClick={handleLogout}>Sign out</button>
        </div>
      </header>

      {/* Add Lead Form */}
      <section className="card">
        <h2>Add New Lead</h2>
        <form onSubmit={handleSubmit} className="lead-form">
          <div className="form-row">
            <div className="field">
              <label>Name *</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Full name"
                required
              />
            </div>
            <div className="field">
              <label>Email *</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="email@example.com"
                required
              />
            </div>
            <div className="field">
              <label>Phone</label>
              <input
                type="text"
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                placeholder="+62 812 ..."
              />
            </div>
            <div className="field">
              <label>Budget (USD)</label>
              <input
                type="number"
                min="0"
                step="1000"
                value={form.budget}
                onChange={(e) => setForm({ ...form, budget: e.target.value })}
                placeholder="e.g. 250000"
              />
            </div>
          </div>
          <div className="field">
            <label>Notes</label>
            <textarea
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
              placeholder="Any additional notes..."
              rows={2}
            />
          </div>
          {formError && <p className="error-msg">{formError}</p>}
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Adding...' : 'Add Lead'}
          </button>
        </form>
      </section>

      {/* Filter Tabs + Table */}
      <section className="card">
        <div className="filter-bar">
          <span className="filter-label">Filter:</span>
          <button
            className={`filter-btn ${statusFilter === '' ? 'active' : ''}`}
            onClick={() => setStatusFilter('')}
          >
            All
          </button>
          {STATUSES.map((s) => (
            <button
              key={s}
              className={`filter-btn ${statusFilter === s ? 'active' : ''}`}
              onClick={() => setStatusFilter(s)}
              style={statusFilter === s ? { background: STATUS_COLORS[s], borderColor: STATUS_COLORS[s] } : {}}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="empty-state">Loading...</p>
        ) : leads.length === 0 ? (
          <p className="empty-state">No leads found.</p>
        ) : (
          <div className="table-wrap">
            <table className="leads-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Budget</th>
                  <th>Status</th>
                  <th>Notes</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead) => (
                  <tr key={lead.id}>
                    <td>{lead.name}</td>
                    <td>{lead.email}</td>
                    <td>{lead.phone || '—'}</td>
                    <td>{lead.budget != null ? `$${lead.budget.toLocaleString()}` : '—'}</td>
                    <td><StatusBadge status={lead.status} /></td>
                    <td className="notes-cell">{lead.notes || '—'}</td>
                    <td>{new Date(lead.created_at).toLocaleDateString()}</td>
                    <td className="actions-cell">
                      <select
                        value={lead.status}
                        onChange={(e) => handleStatusChange(lead, e.target.value)}
                        className="status-select"
                      >
                        {STATUSES.map((s) => (
                          <option key={s} value={s}>
                            {s.charAt(0).toUpperCase() + s.slice(1)}
                          </option>
                        ))}
                      </select>
                      <button onClick={() => handleDelete(lead.id)} className="btn btn-danger">
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="lead-count">
          Showing {leads.length} lead{leads.length !== 1 ? 's' : ''}
          {statusFilter ? ` — status: "${statusFilter}"` : ''}
        </p>
      </section>
    </div>
  )
}