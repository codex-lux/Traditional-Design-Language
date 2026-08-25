import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Dev: vite serves the app and proxies /api to the Python server, so the browser
// only ever sees one origin and CORS never enters the picture.
// Prod: `npm run build` emits dist/, which the Python server mounts at /.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5177,
    proxy: { '/api': 'http://127.0.0.1:8177' },
  },
  build: { chunkSizeWarningLimit: 900 },
});
