import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { copyFileSync } from 'fs';
import { buildSync } from 'esbuild';

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'extension-post-build',
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

        try {
          // Bundle content-script as standalone IIFE to eliminate ES import statements
          // which are disallowed in Chrome Extension content_scripts
          buildSync({
            entryPoints: [resolve(__dirname, 'src/content/content-script.ts')],
            bundle: true,
            outfile: resolve(__dirname, 'dist', 'src', 'content', 'content-script.js'),
            format: 'iife',
            target: 'es2020',
            minify: true,
          });
          console.log('Successfully bundled standalone content-script.js (IIFE)');
        } catch (e) {
          console.error('Failed to bundle content script:', e);
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
