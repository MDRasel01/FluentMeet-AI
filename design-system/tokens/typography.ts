/**
 * AI Meeting English Coach - Typography Tokens
 */

export const typography = {
  fontFamily: {
    sans: 'Inter, Geist Sans, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    mono: 'Geist Mono, JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace',
    display: 'Geist Sans, Inter, sans-serif',
  },
  fontSize: {
    display: ['36px', { lineHeight: '44px', fontWeight: '700', letterSpacing: '-0.025em' }],
    h1: ['30px', { lineHeight: '38px', fontWeight: '700', letterSpacing: '-0.02em' }],
    h2: ['24px', { lineHeight: '32px', fontWeight: '600', letterSpacing: '-0.015em' }],
    h3: ['20px', { lineHeight: '28px', fontWeight: '600', letterSpacing: '-0.01em' }],
    h4: ['18px', { lineHeight: '26px', fontWeight: '600', letterSpacing: '-0.005em' }],
    bodyLarge: ['16px', { lineHeight: '24px', fontWeight: '400', letterSpacing: '0' }],
    body: ['14px', { lineHeight: '20px', fontWeight: '400', letterSpacing: '0' }],
    small: ['13px', { lineHeight: '18px', fontWeight: '400', letterSpacing: '0' }],
    caption: ['12px', { lineHeight: '16px', fontWeight: '500', letterSpacing: '0.01em' }],
    micro: ['11px', { lineHeight: '14px', fontWeight: '500', letterSpacing: '0.02em' }],
  },
  fontWeight: {
    regular: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
  },
} as const;

export type TypographyTokens = typeof typography;

