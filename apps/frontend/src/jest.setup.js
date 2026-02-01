/// <reference types="@testing-library/jest-dom" />
import '@testing-library/jest-dom'

global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

global.fetch = global.fetch || function() {
  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  });
};

window.matchMedia = window.matchMedia || function () {
  return {
    matches: false,
    addListener() {},
    removeListener() {},
  }
}
