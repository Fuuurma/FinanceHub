import '@testing-library/jest-dom'

// Extend Jest types with testing-library/jest-dom matchers
import type { expect } from '@jest/globals'

// This file ensures TypeScript recognizes jest-dom matchers
// The actual imports are in jest.setup.js

declare module '@jest/expect' {
  interface Matchers<R> {
    toBeInTheDocument(): R
    not: {
      toBeInTheDocument(): R
    }
  }
}
