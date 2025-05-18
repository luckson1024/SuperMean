import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    setupNodeEvents(on, config) {
      require('./cypress/plugins/index.js')(on, config);
      return config;
    },
    supportFile: 'cypress/support/e2e.ts',
  },
  component: {
    devServer: {
      framework: 'next',
      bundler: 'webpack',
    },
  },
  // Polyfill process for async (Cypress 12+)
  env: {
    NODE_OPTIONS: '--require process/browser',
  },
});