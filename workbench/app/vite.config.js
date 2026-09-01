import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Dev: vite serves the app and proxies /api to the Python server, so the browser
// only ever sees one origin and CORS never enters the picture.
// Prod: `npm run build` emits dist/, which the Python server mounts at /.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5177,
    // `/corpus` as well as `/api`: the generated plates are served from the corpus mount, and
    // under `npm run dev` every <img src="/corpus/assets/generated/..."> hit Vite and missed.
    proxy: { '/api': 'http://127.0.0.1:8177', '/corpus': 'http://127.0.0.1:8177' },
  },
  build: { chunkSizeWarningLimit: 900 },
});
