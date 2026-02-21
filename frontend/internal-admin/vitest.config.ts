import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/**/*.{test,spec}.{js,ts,jsx,tsx,vue}'],
    exclude: ['**/node_modules/**', '**/dist/**', '**/*.d.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/stories/',
        '**/*.d.ts',
        '**/*.{test,spec}.{js,ts,jsx,tsx,vue}',
        '**/index.{js,ts}'
      ],
      threshold: {
        statements: 70,
        branches: 70,
        functions: 70,
        lines: 70
      }
    },
    transformMode: {
      web: [/\.[jt]sx$/, /\.vue$/]
    },
    server: {
      deps: {
        inline: ['element-plus']
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  }
})
