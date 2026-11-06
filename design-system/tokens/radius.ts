/**
 * AI Meeting English Coach - Border Radius Tokens
 */

export const radius = {
  none: '0px',
  xs: '4px',     // Micro inputs, tooltips, tags
  sm: '6px',     // Compact buttons, badges
  md: '8px',     // Default inputs, cards, dropdowns
  lg: '12px',    // Modal dialogs, large feature cards
  xl: '16px',    // Panels, drawer corners
  '2xl': '20px', // Floating banners
  full: '9999px',// Avatars, pills, circular buttons
} as const;

export type RadiusTokens = typeof radius;

