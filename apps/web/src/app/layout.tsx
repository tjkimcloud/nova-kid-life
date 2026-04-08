import type { Metadata } from 'next'
import { GoogleAnalytics } from '@next/third-parties/google'
import { nunito, plusJakarta, dmSans } from '@/lib/fonts'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default:  'NovaKidLife — Family Events in Northern Virginia',
    template: '%s | NovaKidLife',
  },
  description:
    'Discover the best family events, kids activities, and things to do in Northern Virginia. Fairfax, Arlington, Loudoun, and Prince William counties.',
  metadataBase: new URL('https://novakidlife.com'),
  openGraph: {
    siteName: 'NovaKidLife',
    locale:   'en_US',
    type:     'website',
    images: [{
      url:    'https://novakidlife.com/images/hero-family-meadow-v2.jpg',
      width:  1200,
      height: 630,
      alt:    'Family enjoying outdoor activities in Northern Virginia',
    }],
  },
  twitter: {
    card:   'summary_large_image',
    images: ['https://novakidlife.com/images/hero-family-meadow-v2.jpg'],
  },
  robots: {
    index:  true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en"
      className={`${nunito.variable} ${plusJakarta.variable} ${dmSans.variable}`}
    >
      <body className="font-body antialiased min-h-screen flex flex-col">
        <Header />
        <div className="flex-1">
          {children}
        </div>
        <Footer />
      </body>
      <GoogleAnalytics gaId="G-4S80ZKSG0C" />
    </html>
  )
}
