import type { Metadata } from 'next'
import { nunito, plusJakarta } from '@/lib/fonts'
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
  },
  twitter: {
    card: 'summary_large_image',
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
      className={`${nunito.variable} ${plusJakarta.variable}`}
    >
      <body className="font-body antialiased min-h-screen flex flex-col">
        <Header />
        <div className="flex-1">
          {children}
        </div>
        <Footer />
      </body>
    </html>
  )
}
