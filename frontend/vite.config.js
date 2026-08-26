import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'prompt',
      manifest: {
        name: 'Rental Management System',
        short_name: 'RentManager',
        description: 'Manage properties, tenants, rent, payments and maintenance',
        theme_color: '#1a5c2a',
        background_color: '#f9fafb',
        display: 'standalone',
        start_url: '/dashboard',
        scope: '/',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          // Cache GET API responses with NetworkFirst so fresh data is preferred
          // but cached data is served when offline
          {
            urlPattern: /\/api\/(properties|units|tenants|tenancies|payments|maintenance|expenses|notifications|reports\/dashboard)(.*)/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-reads-cache',
              expiration: { maxEntries: 200, maxAgeSeconds: 86400 },
              networkTimeoutSeconds: 5,
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          // Reports and operational reads use stale-while-revalidate for moderate freshness
          {
            urlPattern: /\/api\/(ledger|reports)(.*)/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'api-secondary-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 3600 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8003',
        changeOrigin: true,
      },
    },
  },
})
