import { defineConfig } from 'vite';
import autoprefixer from 'autoprefixer';
import { resolve } from 'node:path';

// Сборка ассетов темы WordPress.
// Выход — assets/dist/, оттуда подключается через wp_enqueue_* в inc/assets.php.
export default defineConfig({
  build: {
    outDir: 'assets/dist',
    emptyOutDir: true,
    manifest: true,
    sourcemap: process.env.NODE_ENV !== 'production',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'assets/scss/main.scss'),
        app:  resolve(__dirname, 'assets/js/main.js'),
      },
      output: {
        entryFileNames: 'js/[name].js',
        chunkFileNames: 'js/[name].js',
        assetFileNames: (info) => {
          if (/\.css$/.test(info.name ?? '')) return 'css/[name][extname]';
          if (/\.(woff2?|ttf|otf)$/.test(info.name ?? '')) return 'fonts/[name][extname]';
          return 'img/[name][extname]';
        },
      },
    },
    cssMinify: 'lightningcss',
  },
  css: {
    preprocessorOptions: {
      scss: {
        // Dart Sass, современный API. @import не используем.
        api: 'modern-compiler',
        // Пути для @use 'mdb-ui-kit/...'
        loadPaths: ['node_modules'],
      },
    },
    postcss: {
      plugins: [autoprefixer()],
    },
  },
  resolve: {
    alias: {
      '@scss': resolve(__dirname, 'assets/scss'),
      '@js':   resolve(__dirname, 'assets/js'),
    },
  },
});
