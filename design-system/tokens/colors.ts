/**
 * AI Meeting English Coach - Color Tokens
 * Single Source of Truth for all color values across Web, Extension & Admin
 */

export const colors = {
  // Primary Brand Palette
  primary: {
    50: '#EEF2FF',   // Soft Background / Selected tints
    100: '#E0E7FF',  // Hover tint / Secondary highlights
    200: '#C7D2FE',  // Light border
    300: '#A5B4FC',  // Accent border
    400: '#818CF8',  // Active accent
    500: '#6366F1',  // Primary Brand CTA
    600: '#4F46E5',  // Hover State
    700: '#4338CA',  // Active / Pressed State
    800: '#3730A3',  // Dark accent
    900: '#312E81',  // Deep contrast
    950: '#1E1B4B',  // Dark theme soft tint
  },

  // Neutral Palette (Grays / Slates)
  neutral: {
    0: '#FFFFFF',    // Pure White surface
    50: '#F8FAFC',   // Light theme application background
    100: '#F1F5F9',  // Subtle secondary background
    200: '#E2E8F0',  // Standard border
    300: '#CBD5E1',  // Disabled border / Muted divider
    400: '#94A3B8',  // Placeholder text / Inactive icons
    500: '#64748B',  // Secondary / Supporting text
    600: '#475569',  // Body text variant
    700: '#334155',  // Primary body text
    800: '#1E293B',  // High contrast subtitle
    900: '#0F172A',  // Primary page headings
    950: '#020617',  // Deepest slate
  },

  // Semantic Status Palette
  status: {
    success: {
      DEFAULT: '#16A34A',
      soft: '#DCFCE7',
      border: '#86EFAC',
      text: '#14532D',
    },
    warning: {
      DEFAULT: '#D97706',
      soft: '#FEF3C7',
      border: '#FCD34D',
      text: '#78350F',
    },
    danger: {
      DEFAULT: '#DC2626',
      soft: '#FEE2E2',
      border: '#FCA5A5',
      text: '#7F1D1D',
    },
    info: {
      DEFAULT: '#2563EB',
      soft: '#DBEAFE',
      border: '#93C5FD',
      text: '#1E3A8A',
    },
  },

  // Dark Theme Dedicated Tokens
  dark: {
    background: '#0B1020',
    surface: '#111827',
    elevatedSurface: '#1F2937',
    subtle: '#172033',
    border: '#334155',
    borderSubtle: '#273449',
    heading: '#F8FAFC',
    body: '#CBD5E1',
    muted: '#94A3B8',
    disabled: '#475569',
  },
} as const;

export type ColorTokens = typeof colors;

