import { describe, it, expect } from 'vitest';
import { platformDetector } from '../../src/platforms/platform-detector';
import { GoogleMeetAdapter } from '../../src/platforms/google-meet/google-meet-adapter';
import { ZoomWebAdapter } from '../../src/platforms/zoom/zoom-adapter';
import { MicrosoftTeamsAdapter } from '../../src/platforms/microsoft-teams/teams-adapter';

describe('Platform Detection Engine (Section 6)', () => {
  const gmeet = new GoogleMeetAdapter();
  const zoom = new ZoomWebAdapter();
  const teams = new MicrosoftTeamsAdapter();

  it('should accurately match Google Meet meeting URLs and reject non-meeting URLs', () => {
    expect(gmeet.matchesUrl('https://meet.google.com/abc-defg-hij')).toBe(true);
    expect(gmeet.matchesUrl('https://meet.google.com/xyz-pqrs-tuv?authuser=0')).toBe(true);
    // Non-meeting Google URLs
    expect(gmeet.matchesUrl('https://meet.google.com/landing')).toBe(false);
    expect(gmeet.matchesUrl('https://google.com/search?q=meet')).toBe(false);
  });

  it('should accurately match Zoom Web client URLs and reject non-meeting Zoom pages', () => {
    expect(zoom.matchesUrl('https://app.zoom.us/wc/1234567890/join')).toBe(true);
    expect(zoom.matchesUrl('https://us02web.zoom.us/j/9876543210')).toBe(true);
    // Non-meeting Zoom URLs
    expect(zoom.matchesUrl('https://zoom.us/pricing')).toBe(false);
    expect(zoom.matchesUrl('https://zoom.us/signin')).toBe(false);
  });

  it('should accurately match Microsoft Teams Web meetings and reject non-meeting Teams pages', () => {
    expect(teams.matchesUrl('https://teams.microsoft.com/v2/meet/123456')).toBe(true);
    expect(teams.matchesUrl('https://teams.microsoft.com/_#/modern-calling/call-123')).toBe(true);
    // Non-meeting Teams URLs
    expect(teams.matchesUrl('https://teams.microsoft.com/_#/conversations')).toBe(false);
  });

  it('should detect platform types via unified platform detector', () => {
    expect(platformDetector.detectPlatformType('https://meet.google.com/abc-defg-hij')).toBe('google-meet');
    expect(platformDetector.detectPlatformType('https://app.zoom.us/wc/1234567890')).toBe('zoom');
    expect(platformDetector.detectPlatformType('https://teams.microsoft.com/meet/123')).toBe('teams');
    expect(platformDetector.detectPlatformType('https://example.com')).toBe('unknown');
  });
});

