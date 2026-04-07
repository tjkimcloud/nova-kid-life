// Type declaration for GA4 gtag — added by @next/third-parties/google
interface Window {
  gtag?: (
    command: 'event' | 'config' | 'set',
    target: string,
    params?: Record<string, unknown>,
  ) => void
}
