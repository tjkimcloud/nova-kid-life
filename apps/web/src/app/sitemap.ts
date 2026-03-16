import type { MetadataRoute } from 'next'

const BASE_URL = 'https://novakidlife.com'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date()

  const staticPages: MetadataRoute.Sitemap = [
    {
      url:             BASE_URL,
      lastModified:    now,
      changeFrequency: 'daily',
      priority:        1.0,
    },
    {
      url:             `${BASE_URL}/events`,
      lastModified:    now,
      changeFrequency: 'daily',
      priority:        0.8,
    },
    {
      url:             `${BASE_URL}/pokemon`,
      lastModified:    now,
      changeFrequency: 'daily',
      priority:        0.8,
    },
    {
      url:             `${BASE_URL}/pokemon/drops`,
      lastModified:    now,
      changeFrequency: 'daily',
      priority:        0.8,
    },
    {
      url:             `${BASE_URL}/about`,
      lastModified:    now,
      changeFrequency: 'monthly',
      priority:        0.4,
    },
  ]

  try {
    const API  = (process.env.NEXT_PUBLIC_API_URL ?? '').replace(/\/$/, '')
    const data = await fetch(`${API}/sitemap`, { cache: 'no-store' }).then((r) => r.json())

    const mainSlugs:    string[] = data.main    ?? []
    const pokemonSlugs: string[] = data.pokemon ?? []

    const eventPages: MetadataRoute.Sitemap = [
      ...mainSlugs.map((slug) => ({
        url:             `${BASE_URL}/events/${slug}`,
        changeFrequency: 'weekly' as const,
        priority:        0.6,
      })),
      ...pokemonSlugs.map((slug) => ({
        url:             `${BASE_URL}/pokemon/events/${slug}`,
        changeFrequency: 'weekly' as const,
        priority:        0.6,
      })),
    ]

    return [...staticPages, ...eventPages]
  } catch {
    return staticPages
  }
}
