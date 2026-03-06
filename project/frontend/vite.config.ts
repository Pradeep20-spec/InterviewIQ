import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  build: {
    // Raise the warning threshold — our chunks are expected assets (jsPDF, html2canvas)
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      output: {
        // Split heavy third-party libraries into separate cacheable chunks
        manualChunks: {
          'vendor-react':    ['react', 'react-dom'],
          'vendor-pdf':      ['jspdf', 'html2canvas'],
          'vendor-icons':    ['lucide-react'],
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Forward all /api requests to the FastAPI backend during development
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
