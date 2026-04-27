import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { getCollection } from 'astro:content';
import { SITE } from '../config';

export async function GET(context: APIContext) {
  const posts = await getCollection('blog', ({ data }) => {
    return !data.draft;
  });

  const sortedPosts = posts
    .filter((post) => post.slug.startsWith('en/'))
    .sort(
      (a, b) =>
        b.data.publishDate.valueOf() - a.data.publishDate.valueOf()
    );

  return rss({
    title: SITE.name,
    description: SITE.description,
    site: context.site!,
    items: sortedPosts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.publishDate,
      description: post.data.description,
      link: `/blog/${post.slug.replace('en/', '')}`,
      categories: [post.data.category, ...post.data.tags],
      author: post.data.author,
    })),
    customData: `<language>en-us</language>`,
  });
}
