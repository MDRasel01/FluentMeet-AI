import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@design-system': path.resolve(__dirname, './design-system'),
      '@apps': path.resolve(__dirname, './apps'),
    },
  },
  server: {
    port: 3000,
  },
});

