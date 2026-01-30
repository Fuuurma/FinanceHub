const { transformSync } = require('@swc/core')

module.exports = {
  process(source, filename) {
    const result = transformSync(source, {
      filename,
      jsc: {
        parser: {
          syntax: 'typescript',
          tsx: filename.endsWith('.tsx'),
        },
        transform: {
          react: {
            runtime: 'automatic',
          },
        },
      },
      module: {
        type: 'commonjs',
      },
    })
    return {
      code: result.code,
    }
  },
}
