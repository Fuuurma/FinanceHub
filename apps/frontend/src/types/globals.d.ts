// Type declarations for Jest and testing-library/jest-dom
// This file extends TypeScript's understanding of Jest matchers

/// <reference types="@testing-library/jest-dom" />

// Extend global expect with jest-dom matchers
declare global {
  namespace jest {
    interface Matchers<T> {
      toBeInTheDocument(): T
      toBeVisible(): T
      toBeHidden(): T
      toBeDisabled(): T
      toBeEnabled(): T
      toBeEmpty(): T
      toBeChecked(): T
      toHaveTextContent(text: string | RegExp): T
      toHaveAttribute(attr: string, value?: string): T
      toHaveClass(className: string): T
      toHaveValue(value?: string | number | string[]): T
      toHaveFocus(): T
      toBeInTheDocument(): T
    }
  }
}

export {}
