const nextJest = require('next/jest')

const createJestConfig = nextJest({
  moduleDirectories: ['node_modules', '<rootDir>'],
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
})

const config = createJestConfig({
  moduleDirectories: ['node_modules', '<rootDir>'],
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': ['babel-jest', { configFile: '<rootDir>/babel.config.js' }],
  },
  transformIgnorePatterns: [
    '/node_modules/(?!@babel)',
  ],
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx'],
})

module.exports = config
