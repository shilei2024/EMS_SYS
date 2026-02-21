import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import StatCard from '../components/StatCard.vue'
import { ElIcon } from 'element-plus'

describe('StatCard Component', () => {
  it('should render with default props', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '测试标签',
        value: 100
      },
      global: {
        components: {
          ElIcon
        }
      }
    })

    expect(wrapper.text()).toContain('测试标签')
    expect(wrapper.text()).toContain('100')
  })

  it('should render with custom color', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '自定义颜色',
        value: 200,
        color: '#67C23A'
      },
      global: {
        components: {
          ElIcon
        }
      }
    })

    const card = wrapper.find('.stat-card')
    expect(card.attributes('style')).toContain('#67C23A')
  })

  it('should format large numbers', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '大数值',
        value: 100000000
      },
      global: {
        components: {
          ElIcon
        }
      }
    })

    expect(wrapper.text()).toContain('1.00 亿')
  })

  it('should show trend when provided', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '趋势',
        value: 500,
        trend: 15
      },
      global: {
        components: {
          ElIcon
        }
      }
    })

    expect(wrapper.text()).toContain('15%')
    expect(wrapper.find('.stat-trend.up').exists()).toBe(true)
  })

  it('should show negative trend', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '负趋势',
        value: 500,
        trend: -10
      },
      global: {
        components: {
          ElIcon
        }
      }
    })

    expect(wrapper.find('.stat-trend.down').exists()).toBe(true)
  })
})
