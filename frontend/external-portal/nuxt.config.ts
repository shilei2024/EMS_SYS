// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@pinia/nuxt'
  ],

  css: [
    'element-plus/dist/index.css'
  ],

  vite: {
    optimizeDeps: {
      include: ['element-plus']
    },
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vue-vendor': ['vue', 'vue-router', 'pinia'],
            'element-plus': ['element-plus', '@element-plus/icons-vue']
          }
        }
      }
    }
  },

  app: {
    head: {
      title: '电子元器件商城',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '专业的电子元器件供应商，提供 IC 芯片、传感器、连接器等电子产品' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    },
    // 页面过渡动画
    pageTransition: { name: 'page', mode: 'out-in' }
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8001'
    }
  },

  routeRules: {
    // 首页预渲染
    '/': { prerender: true },
    // 关于我们静态页
    '/about': { prerender: true },
    // 产品页 SSR
    '/products': { ssr: true },
    // 登录注册页 SPA 模式
    '/login': { ssr: false },
    '/register': { ssr: false },
    '/profile': { ssr: false },
    '/checkout': { ssr: false }
  },

  nitro: {
    compressPublicAssets: {
      gzip: true,
      brotli: true
    },
    // 静态资源缓存
    routeRules: {
      '/**/*.{js,css,png,jpg,jpeg,svg,webp}': {
        headers: {
          'Cache-Control': 'public, max-age=31536000, immutable'
        }
      }
    }
  },

  typescript: {
    strict: true,
    tsConfig: {
      compilerOptions: {
        baseUrl: '.',
        paths: {
          '@/*': ['./*']
        }
      }
    }
  },

  // 性能优化
  optimization: {
    // 组件懒加载
    lazyHydrate: true
  },

  // 图像优化
  image: {
    provider: 'ipx',
    screens: {
      xs: 320,
      sm: 640,
      md: 768,
      lg: 1024,
      xl: 1280
    }
  }
})
