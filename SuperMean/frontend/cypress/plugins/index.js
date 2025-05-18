const webpack = require('webpack');

module.exports = (on, config) => {
  on('file:preprocessor', require('@cypress/webpack-preprocessor')({
    webpackOptions: {
      resolve: {
        fallback: {
          process: require.resolve('process/browser'),
        },
      },
      plugins: [
        new webpack.ProvidePlugin({
          process: 'process/browser',
        }),
      ],
    },
  }));
  return config;
};
