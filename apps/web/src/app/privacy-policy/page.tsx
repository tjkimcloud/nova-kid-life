import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Privacy Policy — NovaKidLife',
  description: 'NovaKidLife privacy policy — how we handle your data.',
  alternates: { canonical: 'https://novakidlife.com/privacy-policy' },
  robots: { index: false, follow: false },
}

export default function PrivacyPolicyPage() {
  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-16">

        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-8">
          <ol className="flex items-center gap-2 text-sm text-secondary-400">
            <li><Link href="/" className="hover:text-primary-600 transition-colors">Home</Link></li>
            <li aria-hidden="true">/</li>
            <li className="text-secondary-700 font-medium" aria-current="page">Privacy Policy</li>
          </ol>
        </nav>

        <h1 className="font-heading font-extrabold text-4xl text-secondary-900 mb-2">
          Privacy Policy
        </h1>
        <p className="text-sm text-secondary-400 mb-10">Last updated: March 2026</p>

        <div className="prose prose-secondary max-w-none text-secondary-700 leading-relaxed space-y-6">

          <p>
            NovaKidLife (&ldquo;we&rdquo;, &ldquo;us&rdquo;, &ldquo;our&rdquo;) operates novakidlife.com.
            This page explains what data we collect and how we use it.
          </p>

          <h2 className="font-heading font-bold text-xl text-secondary-900">What we collect</h2>
          <p>
            <strong>Newsletter subscriptions:</strong> If you subscribe to our newsletter, we collect
            your email address. We use it only to send you the NovaKidLife newsletter. We never
            sell or share your email with third parties.
          </p>
          <p>
            <strong>Usage analytics:</strong> We may use privacy-friendly analytics (such as
            Plausible Analytics) to understand aggregate traffic patterns — pages visited, referral
            sources, and general geographic region. No personally identifiable information is
            collected. No cookies are set for analytics.
          </p>
          <p>
            <strong>Event data:</strong> All event information on this site is sourced from publicly
            available sources (library websites, Eventbrite, Meetup, etc.). We do not collect any
            data from event organizers or attendees.
          </p>

          <h2 className="font-heading font-bold text-xl text-secondary-900">Cookies</h2>
          <p>
            NovaKidLife does not use tracking cookies or advertising cookies. We do not use
            Google Analytics, Meta Pixel, or any other third-party tracking.
          </p>

          <h2 className="font-heading font-bold text-xl text-secondary-900">Third-party links</h2>
          <p>
            Event pages link to third-party websites (library systems, Eventbrite, Meetup, venue
            websites). We are not responsible for the privacy practices of those sites.
          </p>

          <h2 className="font-heading font-bold text-xl text-secondary-900">Your rights</h2>
          <p>
            If you subscribed to our newsletter and would like to unsubscribe or have your email
            removed, email us at{' '}
            <a
              href="mailto:hello@novakidlife.com"
              className="text-primary-600 hover:text-primary-700 underline"
            >
              hello@novakidlife.com
            </a>{' '}
            and we will remove you within 48 hours.
          </p>

          <h2 className="font-heading font-bold text-xl text-secondary-900">Contact</h2>
          <p>
            Questions about this policy:{' '}
            <a
              href="mailto:hello@novakidlife.com"
              className="text-primary-600 hover:text-primary-700 underline"
            >
              hello@novakidlife.com
            </a>
          </p>

        </div>

      </div>
    </main>
  )
}
