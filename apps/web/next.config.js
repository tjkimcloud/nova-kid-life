/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true, // required for static export
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'media.novakidlife.com',
      },
    ],
  },
  // Font cache headers are set by CloudFront in production (headers() not supported with static export)
}

module.exports = nextConfig
