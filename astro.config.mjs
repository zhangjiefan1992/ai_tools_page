import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import rehypeAdInjector from './src/plugins/rehype-ad-injector';

export default defineConfig({
  site: process.env.SITE_URL || 'https://your-domain.com',
  output: 'static',
  trailingSlash: 'never',
  compressHTML: true,
  integrations: [
    tailwind(),
    sitemap({
      filter: (page) => !page.includes('/404'),
      serialize: (item) => {
        if (item.url.includes('/blog/')) {
          item.changefreq = 'weekly';
          item.priority = 0.8;
        } else if (item.url.endsWith('/')) {
          item.changefreq = 'daily';
          item.priority = 1.0;
        } else {
          item.changefreq = 'monthly';
          item.priority = 0.5;
        }
        return item;
      },
    }),
  ],
  markdown: {
    rehypePlugins: [
      [rehypeAdInjector, {
        paragraphInterval: 3,
        maxAds: 3,
        minParagraphs: 6,
      }],
    ],
    shikiConfig: {
      theme: 'github-light',
      wrap: true,
    },
  },
  vite: {
    build: {
      cssMinify: true,
    },
  },
  build: {
    inlineStylesheets: 'auto',
  },
});
