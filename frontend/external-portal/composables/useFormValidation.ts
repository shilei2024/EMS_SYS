/**
 * 表单验证组合式函数
 * 提供常用的表单验证规则
 */

import { sanitizeInput, validateEmail, validatePhone, validatePassword } from '~/utils/security'

interface ValidationRule {
  required?: boolean
  message?: string
  trigger?: 'blur' | 'change' | 'submit'
  pattern?: RegExp
  min?: number
  max?: number
  validator?: (value: any) => boolean | string
}

interface ValidationRules {
  [key: string]: ValidationRule[]
}

// 用户名验证
export function usernameRules(): ValidationRule[] {
  return [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3-20 个字符', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/,
      message: '用户名只能包含字母、数字和下划线，且以字母开头',
      trigger: 'blur'
    }
  ]
}

// 密码验证
export function passwordRules(): ValidationRule[] {
  return [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 位', trigger: 'blur' },
    {
      validator: (value: string) => {
        const result = validatePassword(value)
        return result.valid ? true : result.message
      },
      trigger: 'blur'
    }
  ]
}

// 邮箱验证
export function emailRules(): ValidationRule[] {
  return [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    {
      validator: (value: string) => {
        return validateEmail(value) ? true : '请输入正确的邮箱格式'
      },
      trigger: 'blur'
    }
  ]
}

// 手机号验证
export function phoneRules(): ValidationRule[] {
  return [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    {
      validator: (value: string) => {
        return validatePhone(value) ? true : '请输入正确的手机号'
      },
      trigger: 'blur'
    }
  ]
}

// 验证码验证
export function codeRules(length = 6): ValidationRule[] {
  return [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    {
      pattern: new RegExp(`^\\d{${length}}$`),
      message: `验证码为${length}位数字`,
      trigger: 'blur'
    }
  ]
}

// 地址验证
export function addressRules(): ValidationRule[] {
  return [
    { required: true, message: '请输入地址', trigger: 'blur' },
    { min: 5, max: 200, message: '地址长度在 5-200 个字符', trigger: 'blur' }
  ]
}

// 真实姓名验证
export function realNameRules(): ValidationRule[] {
  return [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度在 2-20 个字符', trigger: 'blur' },
    {
      pattern: /^[\u4e00-\u9fa5a-zA-Z]+$/,
      message: '姓名只能包含中文或英文',
      trigger: 'blur'
    }
  ]
}

// 确认密码验证
export function confirmPasswordRules(getPassword: () => string): ValidationRule[] {
  return [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (value: string) => {
        return value === getPassword() ? true : '两次输入的密码不一致'
      },
      trigger: 'blur'
    }
  ]
}

// 协议勾选验证
export function agreementRules(message = '请同意用户协议'): ValidationRule[] {
  return [
    {
      validator: (value: boolean) => {
        return value ? true : message
      },
      trigger: 'change'
    }
  ]
}

// 自定义验证器工厂
export function createValidator(
  validatorFn: (value: any) => boolean | string,
  message: string,
  trigger: 'blur' | 'change' | 'submit' = 'blur'
): ValidationRule[] {
  return [
    {
      validator: (value: any) => {
        const result = validatorFn(value)
        return result === true ? true : (typeof result === 'string' ? result : message)
      },
      trigger
    }
  ]
}

// 清理并验证输入
export function sanitizeAndValidate(
  value: string,
  rules: ValidationRule[]
): { valid: boolean; value: string; errors: string[] } {
  const sanitized = sanitizeInput(value)
  const errors: string[] = []

  for (const rule of rules) {
    if (rule.required && !sanitized) {
      errors.push(rule.message || '此项为必填项')
      continue
    }

    if (rule.min && sanitized.length < rule.min) {
      errors.push(rule.message || `长度不能少于${rule.min}个字符`)
      continue
    }

    if (rule.max && sanitized.length > rule.max) {
      errors.push(rule.message || `长度不能多于${rule.max}个字符`)
      continue
    }

    if (rule.pattern && !rule.pattern.test(sanitized)) {
      errors.push(rule.message || '格式不正确')
      continue
    }

    if (rule.validator) {
      const result = rule.validator(sanitized)
      if (result !== true) {
        errors.push(typeof result === 'string' ? result : rule.message || '验证失败')
      }
    }
  }

  return {
    valid: errors.length === 0,
    value: sanitized,
    errors
  }
}
