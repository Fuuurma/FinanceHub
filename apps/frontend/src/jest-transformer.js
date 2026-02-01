const babel = require('@babel/core');

module.exports = {
  process(source, filename) {
    if (filename.includes('__mocks__')) {
      return { code: source };
    }

    const result = babel.transformSync(source, {
      filename,
      plugins: ['@babel/plugin-syntax-typescript'],
      presets: [
        ['@babel/preset-env', { targets: { node: 'current' } }],
        ['@babel/preset-react', { runtime: 'automatic' }],
        ['@babel/preset-typescript', { allowNamespaces: true }],
      ],
    });
    return {
      code: result.code,
    };
  },
};
