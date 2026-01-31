import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const CSP_POLICY = `
  default-src 'self';
  script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.google.com https://www.gstatic.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  img-src 'self' data: https: blob:;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.financehub.app wss://ws.financehub.app https://*.finnhub.io https://*.coingecko.com;
  frame-src 'self';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  upgrade-insecure-requests;
`.trim().replace(/\s+/g, ' ').trim()

const SECURITY_HEADERS = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
}

export function middleware(request: NextRequest) {
  const response = NextResponse.next()

  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')

  const cspHeader = CSP_POLICY.replace("'self'", `'self' 'nonce-${nonce}'`)

  response.headers.set('Content-Security-Policy', cspHeader)
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')

  const hostname = request.headers.get('host') || ''
  if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
    response.headers.set('Strict-Transport-Security', 'max-age=0')
  } else {
    response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')
  }

  response.headers.set('Cross-Origin-Opener-Policy', 'same-origin')
  response.headers.set('Cross-Origin-Resource-Policy', 'same-origin')

  const origin = request.headers.get('origin') || ''
  const allowedOrigins = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://financehub.app',
    'https://www.financehub.app',
  ]

  if (allowedOrigins.includes(origin) || origin.startsWith('http://localhost') || origin.startsWith('http://127.0.0.1')) {
    response.headers.set('Access-Control-Allow-Origin', origin)
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-CSRF-Token, X-Requested-With')
    response.headers.set('Access-Control-Allow-Credentials', 'true')
  }

  if (request.method === 'OPTIONS') {
    response.headers.set('Access-Control-Max-Age', '86400')
    return response
  }

  return response
}

export const config = {
  matcher: [
    '/:path*',
  ],
}
