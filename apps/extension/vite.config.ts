import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { copyFileSync } from 'fs';

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-manifest',
      closeBundle() {
        try {
          copyFileSync(
            resolve(__dirname, 'manifest.json'),
            resolve(__dirname, 'dist', 'manifest.json')
          );
          console.log('Copied manifest.json to dist/');
        } catch (e) {
          console.error('Failed to copy manifest.json:', e);
        }
      }
    }
  ],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        sidepanel: resolve(__dirname, 'sidepanel.html'),
        background: resolve(__dirname, 'src/background/service-worker.ts'),
        content: resolve(__dirname, 'src/content/content-script.ts'),
        offscreen: resolve(__dirname, 'src/offscreen/offscreen.html'),
        pcmProcessor: resolve(__dirname, 'src/offscreen/audio-worklet/pcm-processor.ts'),
      },
      output: {
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'background') return 'src/background/service-worker.js';
          if (chunkInfo.name === 'content') return 'src/content/content-script.js';
          if (chunkInfo.name === 'pcmProcessor') return 'src/offscreen/audio-worklet/pcm-processor.js';
          return 'assets/[name]-[hash].js';
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
      }
    }
  }
});
