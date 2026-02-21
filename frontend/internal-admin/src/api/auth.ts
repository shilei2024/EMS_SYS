import request from '../utils/request'

interface LoginParams {
  username: string
  password: string
}

interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user_id: string
  username: string
  role: string
}

interface UserInfo {
  id: string
  username: string
  email: string
  fullName: string
  role: string
  department?: string
}

export function login(data: LoginParams) {
  return request({
    url: '/api/v1/login',
    method: 'post',
    data
  }) as Promise<LoginResponse>
}

export function logout() {
  return request({
    url: '/api/v1/logout',
    method: 'post'
  })
}

export function getUserInfo() {
  return request({
    url: '/api/v1/profile',
    method: 'get'
  }) as Promise<UserInfo>
}

export function getUsers(params?: any) {
  return request({
    url: '/api/v1/users',
    method: 'get',
    params
  })
}

export function createUser(data: any) {
  return request({
    url: '/api/v1/users',
    method: 'post',
    data
  })
}

export function updateUser(id: string, data: any) {
  return request({
    url: `/api/v1/users/${id}`,
    method: 'put',
    data
  })
}

export function deleteUser(id: string) {
  return request({
    url: `/api/v1/users/${id}`,
    method: 'delete'
  })
}

export function getRoles() {
  return request({
    url: '/api/v1/roles',
    method: 'get'
  })
}

export function toggleUserStatus(id: string, is_active: boolean) {
  return request({
    url: `/api/v1/users/${id}/toggle-status`,
    method: 'post',
    data: { is_active }
  })
}

export function changePassword(id: string, old_password: string, new_password: string) {
  return request({
    url: `/api/v1/users/${id}/change-password`,
    method: 'post',
    data: { old_password, new_password }
  })
}
