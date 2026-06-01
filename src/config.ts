export const SITE = {
  name: 'Pick My AI',
  description: 'Honest reviews, tutorials, and comparisons of the best AI tools to boost your productivity.',
  url: 'https://pick-my-ai.com',
  author: 'Pick My AI Team',
  email: 'contact@pick-my-ai.com',
  language: 'en',
} as const;

export const POSTS_PER_PAGE = 9;

export const CATEGORIES = [
  { slug: 'review', label: 'Reviews', description: 'In-depth reviews of individual AI tools.' },
  { slug: 'comparison', label: 'Comparisons', description: 'Head-to-head comparisons between competing AI tools.' },
  { slug: 'tutorial', label: 'Tutorials', description: 'Step-by-step guides and how-to articles.' },
  { slug: 'best-of', label: 'Best Of', description: 'Curated lists of the best AI tools for specific use cases.' },
] as const;

export const NAV_LINKS = [
  { text: 'Home', href: '/' },
  { text: 'Reviews', href: '/category/review' },
  { text: 'Comparisons', href: '/category/comparison' },
  { text: 'Tutorials', href: '/category/tutorial' },
  { text: 'Best Of', href: '/category/best-of' },
  { text: 'About', href: '/about' },
] as const;

export const SOCIAL_LINKS = [] as const;
