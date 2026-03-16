import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      // All crawlers — allow everything
      { userAgent: '*', allow: '/' },
      // AI crawlers — explicitly welcomed for GEO
      { userAgent: 'GPTBot',        allow: '/' },
      { userAgent: 'PerplexityBot', allow: '/' },
      { userAgent: 'ClaudeBot',     allow: '/' },
      { userAgent: 'Bingbot',       allow: '/' },
      { userAgent: 'Googlebot',     allow: '/' },
      { userAgent: 'OAI-SearchBot', allow: '/' },
      { userAgent: 'cohere-ai',     allow: '/' },
    ],
    sitemap: `${process.env.NEXT_PUBLIC_SITE_URL ?? 'https://novakidlife.com'}/sitemap.xml`,
  }
}
