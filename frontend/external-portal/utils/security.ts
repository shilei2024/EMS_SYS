/**
 * 安全工具模块
 * 提供 XSS 防护、CSRF Token、输入验证等安全功能
 */

// XSS 防护 - 转义 HTML 特殊字符
export function escapeHtml(str: string): string {
  if (!str) return ''
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return str.replace(/[&<>"']/g, (m) => map[m])
}

// XSS 防护 - 还原 HTML 特殊字符
export function unescapeHtml(str: string): string {
  if (!str) return ''
  const map: Record<string, string> = {
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
    '&#039;': "'"
  }
  return str.replace(/&(amp|lt|gt|quot|#039);/g, (m) => map[m])
}

// 清理用户输入，移除潜在的 XSS 攻击代码
export function sanitizeInput(input: string): string {
  if (!input) return ''

  // 转义 HTML
  let sanitized = escapeHtml(input)

  // 移除 javascript: 协议
  sanitized = sanitized.replace(/javascript:/gi, '')

  // 移除 data: 协议（可能用于 XSS）
  sanitized = sanitized.replace(/data\s*:/gi, '')

  // 移除 on* 事件处理器
  sanitized = sanitized.replace(/on\w+\s*=/gi, '')

  return sanitized
}

// 验证邮箱格式
export function validateEmail(email: string): boolean {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email)
}

// 验证手机号格式（中国大陆）
export function validatePhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

// 验证密码强度
export interface PasswordStrength {
  valid: boolean
  strength: 'weak' | 'medium' | 'strong'
  message: string
}

export function validatePassword(password: string): PasswordStrength {
  if (!password || password.length < 6) {
    return {
      valid: false,
      strength: 'weak',
      message: '密码长度至少 6 位'
    }
  }

  let strength = 0
  if (/[a-z]/.test(password)) strength++
  if (/[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++

  if (strength >= 3 && password.length >= 8) {
    return { valid: true, strength: 'strong', message: '强密码' }
  } else if (strength >= 2) {
    return { valid: true, strength: 'medium', message: '中等强度密码' }
  } else {
    return { valid: true, strength: 'weak', message: '弱密码，建议添加大小写字母、数字和特殊字符' }
  }
}

// CSRF Token 管理
export function getCSRFToken(): string | null {
  if (typeof document === 'undefined') return null

  const name = 'csrf_token='
  const decodedCookie = decodeURIComponent(document.cookie)
  const ca = decodedCookie.split(';')

  for (let i = 0; i < ca.length; i++) {
    let c = ca[i].trim()
    if (c.indexOf(name) === 0) {
      return c.substring(name.length)
    }
  }
  return null
}

export function setCSRFToken(token: string, days = 1): void {
  if (typeof document === 'undefined') return

  const expires = new Date()
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000)
  document.cookie = `csrf_token=${token};expires=${expires.toUTCString()};path=/;SameSite=Strict`
}

// 防抖函数（防止频繁请求）
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}

// 节流函数（限制请求频率）
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}

// 验证 URL 是否安全
export function isValidUrl(url: string): boolean {
  try {
    const parsedUrl = new URL(url)
    // 只允许 http 和 https 协议
    return parsedUrl.protocol === 'http:' || parsedUrl.protocol === 'https:'
  } catch {
    return false
  }
}

// 清理 URL，防止 javascript: 协议
export function sanitizeUrl(url: string): string {
  if (isValidUrl(url)) {
    return url
  }
  // 如果是相对路径，直接返回
  if (url.startsWith('/') || url.startsWith('#')) {
    return url
  }
  // 不安全的 URL，返回空字符串
  return ''
}

// 生成随机字符串（用于 Token 等）
export function generateRandomString(length = 32): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

// 敏感信息脱敏
export function maskSensitiveInfo(info: string, type: 'phone' | 'email' | 'id' | 'card'): string {
  if (!info) return ''

  switch (type) {
    case 'phone':
      return info.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
    case 'email':
      const [name, domain] = info.split('@')
      if (name.length <= 2) {
        return `${name[0]}**@${domain}`
      }
      return `${name[0]}${'*'.repeat(name.length - 2)}${name[name.length - 1]}@${domain}`
    case 'id':
      return info.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2')
    case 'card':
      return info.replace(/(\d{4})\d{8}(\d{4})/, '$1********$2')
    default:
      return info
  }
}
