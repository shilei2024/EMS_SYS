import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import StatCard from './StatCard.vue'

describe('StatCard Component', () => {
  it('should render correctly with props', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '总订单数',
        value: 1234,
        icon: 'Document'
      }
    })

    expect(wrapper.text()).toContain('总订单数')
    expect(wrapper.text()).toContain('1,234')
  })

  it('should apply correct color style', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '总订单数',
        value: 1234,
        color: '#409EFF'
      }
    })

    const card = wrapper.find('.stat-card')
    expect(card.attributes('style')).toContain('border-left-color')
  })

  it('should format large numbers correctly', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '总营收',
        value: 1000000,
        icon: 'Money'
      }
    })

    expect(wrapper.text()).toContain('100.00 万')
  })

  it('should format very large numbers as 亿', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '总营收',
        value: 100000000,
        icon: 'Money'
      }
    })

    expect(wrapper.text()).toContain('1.00 亿')
  })

  it('should show trend when provided', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '总订单数',
        value: 100,
        trend: 15
      }
    })

    expect(wrapper.text()).toContain('15%')
    expect(wrapper.find('.stat-trend.up').exists()).toBe(true)
  })

  it('should show negative trend correctly', () => {
    const wrapper = mount(StatCard, {
      props: {
        label: '总订单数',
        value: 100,
        trend: -10
      }
    })

    expect(wrapper.find('.stat-trend.down').exists()).toBe(true)
  })
})
