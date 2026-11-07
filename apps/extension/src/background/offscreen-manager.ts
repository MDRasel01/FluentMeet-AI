/**
 * FluentMeet AI - Offscreen Document Lifecycle Manager
 * Handles single-instance creation, verification, and closure of Offscreen Documents.
 * Specification: Step 05 - Section 4.2.C
 */

export class OffscreenManager {
  private static OFFSCREEN_PATH = 'src/offscreen/offscreen.html';

  /**
   * Ensures an offscreen document is active. If already present, reuses it.
   */
  public static async ensureOffscreenDocument(): Promise<void> {
    if (await this.hasOffscreenDocument()) {
      return;
    }

    await chrome.offscreen.createDocument({
      url: this.OFFSCREEN_PATH,
      reasons: [chrome.offscreen.Reason.USER_MEDIA],
      justification: 'Recording tab audio and microphone audio for meeting English analysis.',
    });
  }

  /**
   * Checks if an offscreen document already exists using chrome.runtime.getContexts.
   */
  public static async hasOffscreenDocument(): Promise<boolean> {
    if (chrome.runtime?.getContexts) {
      const contexts = await chrome.runtime.getContexts({
        contextTypes: [chrome.runtime.ContextType.OFFSCREEN_DOCUMENT],
      });
      return Boolean(contexts && contexts.length > 0);
    }
    return false;
  }

  /**
   * Closes the offscreen document safely.
   */
  public static async closeOffscreenDocument(): Promise<void> {
    if (await this.hasOffscreenDocument()) {
      try {
        await chrome.offscreen.closeDocument();
      } catch (err) {
        console.warn('Error closing offscreen document:', err);
      }
    }
  }
}
