/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
  assetPrefix: process.env.NODE_ENV === 'production'
    ? process.env.NEXT_PUBLIC_CDN_URL || 'https://assets.financehub.app'
    : undefined,
  serverExternalPackages: ['jspdf'],
}

module.exports = nextConfig
