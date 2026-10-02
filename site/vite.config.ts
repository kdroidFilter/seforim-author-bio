import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: './',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
  build: { chunkSizeWarningLimit: 5000 }, // ponytail: all biographies ship in one bundle (~1 MB gz) so a page never depends on a lazy chunk
})
