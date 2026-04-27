import { getCollection } from 'astro:content';

export async function getPublishedPosts() {
  const posts = await getCollection('blog', ({ data, slug }) => {
    return !data.draft && slug.startsWith('en/');
  });

  return posts.sort(
    (a, b) => b.data.publishDate.valueOf() - a.data.publishDate.valueOf()
  );
}

export async function getPostsByCategory(category: string) {
  const posts = await getPublishedPosts();
  return posts.filter((post) => post.data.category === category);
}

export async function getPostsByTag(tag: string) {
  const posts = await getPublishedPosts();
  return posts.filter((post) => post.data.tags.includes(tag));
}

export async function getAllTags(): Promise<string[]> {
  const posts = await getPublishedPosts();
  const tags = new Set(posts.flatMap((post) => post.data.tags));
  return [...tags].sort();
}

export async function getRelatedPosts(
  currentSlug: string,
  category: string,
  tags: string[],
  maxPosts: number = 3
) {
  const posts = await getPublishedPosts();

  return posts
    .filter((post) => post.slug !== currentSlug)
    .map((post) => ({
      ...post,
      relevance:
        (post.data.category === category ? 2 : 0) +
        post.data.tags.filter((t) => tags.includes(t)).length,
    }))
    .sort((a, b) => b.relevance - a.relevance)
    .slice(0, maxPosts);
}
