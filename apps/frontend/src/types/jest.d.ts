import { type TestingLibraryMatchers } from '@testing-library/jest-dom/matchers'

declare module 'expect' {
  interface Matchers<T> extends TestingLibraryMatchers<typeof jest, T> {}
}
