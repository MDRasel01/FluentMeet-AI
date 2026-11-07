/**
 * FluentMeet AI - Unified Platform Detector Engine
 * Orchestrates platform adapters with zero cross-contamination.
 * Specification: Step 05 - Section 6.4
 */

import { PlatformAdapter } from './platform-interface';
import { GoogleMeetAdapter } from './google-meet/google-meet-adapter';
import { ZoomWebAdapter } from './zoom/zoom-adapter';
import { MicrosoftTeamsAdapter } from './microsoft-teams/teams-adapter';
import { MeetingPlatform } from '../types/extension.types';

export class PlatformDetector {
  private adapters: PlatformAdapter[] = [
    new GoogleMeetAdapter(),
    new ZoomWebAdapter(),
    new MicrosoftTeamsAdapter(),
  ];

  public getAdapterForUrl(url: string): PlatformAdapter | null {
    for (const adapter of this.adapters) {
      if (adapter.matchesUrl(url)) {
        return adapter;
      }
    }
    return null;
  }

  public detectPlatformType(url: string): MeetingPlatform {
    const adapter = this.getAdapterForUrl(url);
    return adapter ? adapter.platform : 'unknown';
  }

  public getActiveAdapter(documentContext: Document): PlatformAdapter | null {
    return this.getAdapterForUrl(documentContext.location.href);
  }
}

export const platformDetector = new PlatformDetector();

