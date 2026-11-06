/**
 * FluentMeet AI Chrome Extension Authentication Adapter
 * Manages trusted token storage and background refresh orchestration.
 */

export interface StoredAuthSession {
  accessToken: string;
  refreshToken: string;
  userEmail: string;
  userId: string;
  expiresAt: number;
}

export class ExtensionAuthAdapter {
  private static STORAGE_KEY = 'fluentmeet_auth_session';

  /**
   * Save session into chrome.storage.session (memory-preferred) or local storage.
   */
  static async saveSession(session: StoredAuthSession): Promise<void> {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      if (chrome.storage.session) {
        await chrome.storage.session.set({ [this.STORAGE_KEY]: session });
      } else {
        await chrome.storage.local.set({ [this.STORAGE_KEY]: session });
      }
    }
  }

  /**
   * Retrieve active session token.
   */
  static async getSession(): Promise<StoredAuthSession | null> {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      const storage = chrome.storage.session || chrome.storage.local;
      const data = await storage.get(this.STORAGE_KEY);
      return data[this.STORAGE_KEY] || null;
    }
    return null;
  }

  /**
   * Clear session on logout.
   */
  static async clearSession(): Promise<void> {
    if (typeof chrome !== 'undefined' && chrome.storage) {
      const storage = chrome.storage.session || chrome.storage.local;
      await storage.remove(this.STORAGE_KEY);
    }
  }

  /**
   * Check if token is expired or close to expiring (within 60 seconds).
   */
  static isTokenExpiring(session: StoredAuthSession): boolean {
    return Date.now() >= session.expiresAt - 60000;
  }
}

