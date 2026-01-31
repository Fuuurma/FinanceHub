 /** @type {import('next').NextConfig} */
  const nextConfig = {
    reactStrictMode: true,
    output: 'standalone',
   experimental: {
     optimizePackageImports: ['lucide-react'],
   },
   assetPrefix: process.env.NODE_ENV === 'production'
     ? process.env.NEXT_PUBLIC_CDN_URL || 'https://assets.financehub.app'
     : undefined,
   serverExternalPackages: ['jspdf'],

   // Production optimizations
   compress: true,
   productionBrowserSourceMaps: false,

   // Image optimization
   images: {
     formats: ['image/webp', 'image/avif'],
     deviceSizes: [640, 750, 828, 1080, 1200, 1920],
     imageSizes: [16, 32, 48, 64, 96, 128, 256],
   },

   // Turbopack configuration (Next.js 16+)
   turbopack: {
     // Webpack config will be migrated here in the future
     // For now, use empty config to enable Turbopack
   },

   // Bundle optimization with code splitting (legacy webpack support)
   webpack: (config, { dev, isServer }) => {
    // Production-only optimizations
    if (!dev && !isServer) {
      // Split chunks for better caching
      config.optimization.splitChunks = {
        chunks: 'all',
        minChunks: 1,
        maxInitialRequests: 25,
        minSize: 20000,
        cacheGroups: {
          // Vendor chunk for heavy chart libraries
          echarts: {
            test: /[\\/]node_modules[\\/](echarts|echarts-for-react|echarts-core)[\\/]/,
            name: 'vendor-echarts',
            chunks: 'all',
            priority: 20,
            reuseExistingChunk: true,
          },
          // Vendor chunk for recharts
          recharts: {
            test: /[\\/]node_modules[\\/]recharts[\\/]/,
            name: 'vendor-recharts',
            chunks: 'all',
            priority: 15,
            reuseExistingChunk: true,
          },
          // Vendor chunk for UI components
          ui: {
            test: /[\\/]node_modules[\\/](@radix-ui|class-variance-authority|clsx|tailwind-merge)[\\/]/,
            name: 'vendor-ui',
            chunks: 'all',
            priority: 10,
            reuseExistingChunk: true,
          },
          // Default vendor chunk
          vendors: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all',
            priority: 5,
            reuseExistingChunk: true,
          },
          // Common chunk for shared components
          common: {
            minChunks: 2,
            priority: -5,
            reuseExistingChunk: true,
          },
        },
      }

      // Enable module concatenation for smaller bundles
      config.optimization.usedExports = true
      config.optimization.sideEffects = false
    }

    return config
  },
}

module.exports = nextConfig
