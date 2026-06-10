import { api } from './api'

export const usersService = {
  list({ search = null, role = null, isActive = null, limit = 200 } = {}) {
    const params = new URLSearchParams()
    if (search) params.set('search', String(search))
    if (role) params.set('role', String(role).toUpperCase())
    if (isActive !== null && isActive !== undefined) params.set('is_active', String(Boolean(isActive)))
    params.set('limit', String(limit))
    return api.get(`/users/?${params.toString()}`)
  },

  create(payload) {
    return api.post('/users/', payload)
  },

  updateRole(userId, role) {
    return api.patch(`/users/${userId}/role`, { role })
  },

  updateStatus(userId, isActive) {
    return api.patch(`/users/${userId}/status`, { is_active: Boolean(isActive) })
  },

  resetPassword(userId, password) {
    return api.post(`/users/${userId}/reset-password`, { password })
  },

  resetPin(userId, pin) {
    return api.post(`/users/${userId}/reset-pin`, { pin })
  },

  listActivity({ userId = null, limit = 50 } = {}) {
    const params = new URLSearchParams()
    if (userId) params.set('user_id', userId)
    params.set('limit', String(limit))
    return api.get(`/users/activity?${params.toString()}`)
  },

  listTasks({ assigneeUserId = null, limit = 100 } = {}) {
    const params = new URLSearchParams()
    if (assigneeUserId) params.set('assignee_user_id', assigneeUserId)
    params.set('limit', String(limit))
    return api.get(`/users/tasks?${params.toString()}`)
  },

  listSystemActivity({
    limit = 180,
    action = null,
    resourceType = null,
    actorUserId = null,
    search = null,
    fromAt = null,
    toAt = null,
    period = 'all',
    sort = 'desc',
  } = {}) {
    const params = new URLSearchParams()
    params.set('limit', String(limit))
    if (action) params.set('action', String(action).toUpperCase())
    if (resourceType) params.set('resource_type', String(resourceType).toUpperCase())
    if (actorUserId) params.set('actor_user_id', String(actorUserId))
    if (search) params.set('search', String(search))
    if (fromAt) params.set('from_at', String(fromAt))
    if (toAt) params.set('to_at', String(toAt))
    if (period) params.set('period', String(period).toLowerCase())
    if (sort) params.set('sort', String(sort).toLowerCase())
    return api.get(`/activity-logs/?${params.toString()}`)
  },

  assignTask(payload) {
    return api.post('/users/tasks', payload)
  },

  updateTaskStatus(taskId, isDone) {
    return api.patch(`/users/tasks/${taskId}/status`, { is_done: Boolean(isDone) })
  },
}
