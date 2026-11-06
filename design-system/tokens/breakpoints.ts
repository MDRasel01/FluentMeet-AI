/**
 * AI Meeting English Coach - Responsive Breakpoints
 */

export const breakpoints = {
  smallMobile: '320px',
  mobile: '375px',
  largeMobile: '430px',
  tablet: '768px',
  smallDesktop: '1024px',
  desktop: '1280px',
  largeDesktop: '1440px',
  wideDesktop: '1600px',
} as const;

export type BreakpointTokens = typeof breakpoints;

