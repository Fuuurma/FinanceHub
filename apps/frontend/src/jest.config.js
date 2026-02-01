/** @type {import('jest').Config} */
const path = require('path')

const customJestConfig = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleDirectories: ['node_modules', '<rootDir>'],
  moduleNameMapper: {
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^@/stores/(.*)$': '<rootDir>/stores/$1',
    '^@/hooks/(.*)$': '<rootDir>/hooks/$1',
    '^@/lib/(.*)$': '<rootDir>/lib/$1',
    '^@/(.*)$': '<rootDir>/$1',
    '^@dnd-kit/sortable$': '<rootDir>/__mocks__/@dnd-kit/sortable.js',
    '^@dnd-kit/core$': '<rootDir>/__mocks__/@dnd-kit/core.js',
    '^@dnd-kit/utilities$': '<rootDir>/__mocks__/@dnd-kit/utilities.js',
  },
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': '<rootDir>/jest-transformer.js',
  },
  collectCoverageFrom: [
    '**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/.next/**',
    '!**/coverage/**',
  ],
  testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],
  testPathIgnorePatterns: ['/node_modules/', '/.next/'],
  roots: ['<rootDir>'],
  rootDir: '.',
}

module.exports = customJestConfig
