/**
 * FluentMeet AI Chrome Extension Background Service Worker (Manifest V3)
 */

// Enable opening side panel when clicking the extension action toolbar button
chrome.sidePanel
  ?.setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error: unknown) => console.error("Error setting side panel behavior:", error));

// Listen for runtime extension messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "CHECK_MEETING_STATUS") {
    // Detect active meeting tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs[0];
      const url = activeTab?.url || "";
      let platform = "unknown";
      if (url.includes("meet.google.com")) platform = "google-meet";
      else if (url.includes("zoom.us")) platform = "zoom";
      else if (url.includes("teams.microsoft.com")) platform = "teams";

      sendResponse({
        isMeetingActive: platform !== "unknown",
        platform,
        tabId: activeTab?.id,
        url,
      });
    });
    return true; // Keep message channel open for async response
  }

  if (message.type === "PING") {
    sendResponse({ status: "PONG", timestamp: Date.now() });
  }
});

console.log("[FluentMeet Service Worker] Initialized successfully.");

