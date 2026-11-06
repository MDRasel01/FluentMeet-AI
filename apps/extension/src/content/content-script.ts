/**
 * FluentMeet AI Chrome Extension Content Script
 * Injected into Google Meet, Zoom Web, and MS Teams meetings.
 */

console.log("[FluentMeet Content Script] Loaded on meeting platform:", window.location.hostname);

function detectPlatform(): string {
  const host = window.location.hostname;
  if (host.includes("meet.google.com")) return "google-meet";
  if (host.includes("zoom.us")) return "zoom";
  if (host.includes("teams.microsoft.com")) return "teams";
  return "generic";
}

// Notify background that a meeting session has been detected
chrome.runtime.sendMessage({
  type: "MEETING_PAGE_DETECTED",
  platform: detectPlatform(),
  url: window.location.href,
  title: document.title,
});

