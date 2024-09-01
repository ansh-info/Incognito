const ESLintPlugin = require('eslint-webpack-plugin');

module.exports = {
  webpack: {
    plugins: {
      add: [
        new ESLintPlugin({
          extensions: ['js', 'mjs', 'jsx', 'ts', 'tsx'],
        }),
      ],
    },
  },
  style: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
      ],
    },
  },
};
