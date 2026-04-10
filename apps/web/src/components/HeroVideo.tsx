'use client'

import { useEffect, useRef } from 'react'

interface HeroVideoProps {
  src: string
  poster: string
}

export function HeroVideo({ src, poster }: HeroVideoProps) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            // Set src to trigger load only when in viewport
            if (!video.src) {
              video.src = src
              video.load()
            }
            observer.disconnect()
          }
        }
      },
      { threshold: 0 }
    )

    observer.observe(video)
    return () => observer.disconnect()
  }, [src])

  return (
    <>
      {/* Desktop video — hidden on mobile */}
      <video
        ref={videoRef}
        className="hidden md:block absolute inset-0 w-full h-full object-cover"
        autoPlay
        muted
        loop
        playsInline
        preload="metadata"
        poster={poster}
        aria-hidden="true"
      />

      {/* Mobile static image — shown only under 768px */}
      <div
        className="md:hidden absolute inset-0"
        style={{
          backgroundImage: "url('/images/hero2-legofamily-mobile.png')",
          backgroundSize: 'cover',
          backgroundPosition: '35% center',
          backgroundRepeat: 'no-repeat',
        }}
        aria-hidden="true"
      />
    </>
  )
}
