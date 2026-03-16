'use client'

import { useState } from 'react'

interface BlurImageProps {
  src: string | null
  lqip?: string | null
  alt: string
  width: number
  height: number
  className?: string
  priority?: boolean
}

/**
 * Blur-up image component.
 * Shows LQIP data URL immediately, fades in the full image when loaded.
 * Uses explicit width/height to prevent CLS (Core Web Vitals).
 */
export function BlurImage({
  src,
  lqip,
  alt,
  width,
  height,
  className = '',
  priority = false,
}: BlurImageProps) {
  const [loaded, setLoaded] = useState(false)
  const aspectPadding = `${(height / width) * 100}%`

  const fallback = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='${width}' height='${height}'%3E%3Crect width='100%25' height='100%25' fill='%23FEF3C7'/%3E%3C/svg%3E`
  const placeholder = lqip || fallback

  return (
    <div
      className={`relative overflow-hidden ${className}`}
      style={{ paddingBottom: aspectPadding }}
    >
      {/* LQIP placeholder — visible until full image loads */}
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-cover bg-center scale-110"
        style={{
          backgroundImage: `url('${placeholder}')`,
          filter: loaded ? 'none' : 'blur(8px)',
          transition: 'opacity 0.4s ease, filter 0.4s ease',
          opacity: loaded ? 0 : 1,
        }}
      />

      {/* Full image */}
      {src && (
        <img
          src={src}
          alt={alt}
          width={width}
          height={height}
          loading={priority ? 'eager' : 'lazy'}
          decoding="async"
          onLoad={() => setLoaded(true)}
          className="absolute inset-0 w-full h-full object-cover"
          style={{
            opacity: loaded ? 1 : 0,
            transition: 'opacity 0.4s ease',
          }}
        />
      )}
    </div>
  )
}
