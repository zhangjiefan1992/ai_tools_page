import { defineCollection, z } from 'astro:content';

const categoryEnum = z.enum(['review', 'comparison', 'tutorial', 'best-of']);

const blogCollection = defineCollection({
  type: 'content',
  schema: ({ image }) =>
    z.object({
      title: z
        .string()
        .min(3, 'Title must be at least 3 characters')
        .max(100, 'Title must not exceed 100 characters'),
      description: z
        .string()
        .min(10, 'Description must be at least 10 characters')
        .max(300, 'Description must not exceed 300 characters'),
      publishDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      category: categoryEnum,
      tags: z
        .array(z.string().toLowerCase().trim())
        .min(1, 'At least one tag is required')
        .max(8, 'Maximum 8 tags allowed'),
      author: z.string().default('AI Tools Hub Team'),
      authorAvatar: z.string().url().optional(),
      authorTwitter: z.string().optional(),
      image: z.string().optional(),
      imageAlt: z.string().optional(),
      draft: z.boolean().default(false),
      featured: z.boolean().default(false),
      canonicalURL: z.string().url().optional(),
      ogImage: z.string().optional(),
      robots: z.string().optional(),
      disableAds: z.boolean().default(false),
    }),
});

export const collections = {
  blog: blogCollection,
};
