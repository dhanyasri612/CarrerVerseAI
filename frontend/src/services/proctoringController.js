/**
 * Transparent Browser Integrity & Proctoring Controller
 * Phase 13: Amazon-inspired interview simulation with non-invasive, transparent telemetry.
 *
 * Distinctly decoupled from technical scoring. Events are treated as neutral signals
 * with documented ambiguity (e.g. window blur is not proof of cheating).
 */

import { recordProctoringEvent } from "./careerService";

class ProctoringController {
  constructor() {
    this.sessionId = null;
    this.isActive = false;
    this.onWarning = null;
    this.onStatusChange = null;
    this.hiddenStartTime = null;
    this.screenStream = null;
    this.lastEventTimes = {};
    this.unproctored = false;

    this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
    this.handleBlur = this.handleBlur.bind(this);
    this.handleFocus = this.handleFocus.bind(this);
    this.handleFullscreenChange = this.handleFullscreenChange.bind(this);
    this.handleOffline = this.handleOffline.bind(this);
    this.handleOnline = this.handleOnline.bind(this);
  }

  start({ sessionId, onWarning, onStatusChange, unproctored = false }) {
    if (!sessionId || unproctored) {
      this.unproctored = Boolean(unproctored);
      return;
    }
    this.sessionId = sessionId;
    this.onWarning = onWarning || (() => {});
    this.onStatusChange = onStatusChange || (() => {});
    this.isActive = true;
    this.unproctored = false;

    document.addEventListener("visibilitychange", this.handleVisibilityChange);
    window.addEventListener("blur", this.handleBlur);
    window.addEventListener("focus", this.handleFocus);
    document.addEventListener("fullscreenchange", this.handleFullscreenChange);
    window.addEventListener("offline", this.handleOffline);
    window.addEventListener("online", this.handleOnline);

    this.onStatusChange({
      monitoringActive: true,
      fullscreen: Boolean(document.fullscreenElement),
      online: navigator.onLine,
      screenSharing: Boolean(this.screenStream),
    });
  }

  stop() {
    if (!this.isActive) return;
    this.isActive = false;

    document.removeEventListener("visibilitychange", this.handleVisibilityChange);
    window.removeEventListener("blur", this.handleBlur);
    window.removeEventListener("focus", this.handleFocus);
    document.removeEventListener("fullscreenchange", this.handleFullscreenChange);
    window.removeEventListener("offline", this.handleOffline);
    window.removeEventListener("online", this.handleOnline);

    this.stopScreenShare();
    this.sessionId = null;
  }

  async sendEvent(eventType, durationMs = null, metadata = {}) {
    if (!this.isActive || !this.sessionId || this.unproctored) return;

    // Client-side debounce to avoid duplicate flooding within 500ms
    const now = Date.now();
    const lastTime = this.lastEventTimes[eventType] || 0;
    if (now - lastTime < 500) {
      return;
    }
    this.lastEventTimes[eventType] = now;

    try {
      await recordProctoringEvent(this.sessionId, eventType, durationMs, metadata);
    } catch (err) {
      console.warn(`[Proctoring] Failed to record event ${eventType}:`, err);
    }
  }

  handleVisibilityChange() {
    if (document.hidden) {
      this.hiddenStartTime = Date.now();
      this.sendEvent("visibility_hidden", null, { reason: "tab_hidden" });
      if (typeof this.onWarning === "function") {
        this.onWarning("Interview window lost visibility. Please keep the interview tab in focus.");
      }
    } else {
      const durationMs = this.hiddenStartTime ? Date.now() - this.hiddenStartTime : null;
      this.hiddenStartTime = null;
      this.sendEvent("visibility_visible", durationMs, { reason: "tab_restored" });
    }
  }

  handleBlur() {
    this.sendEvent("window_blur", null, { note: "Window lost focus (ambiguous signal)" });
    if (typeof this.onWarning === "function") {
      this.onWarning("Window lost focus. Please click back into the interview studio.");
    }
  }

  handleFocus() {
    this.sendEvent("window_focus", null, { note: "Window regained focus" });
  }

  handleFullscreenChange() {
    const isFs = Boolean(document.fullscreenElement);
    if (isFs) {
      this.sendEvent("fullscreen_enter", null, {});
    } else {
      this.sendEvent("fullscreen_exit", null, {});
      if (typeof this.onWarning === "function") {
        this.onWarning("Exited full screen mode. You can re-enable full screen anytime.");
      }
    }
    if (typeof this.onStatusChange === "function") {
      this.onStatusChange({ fullscreen: isFs });
    }
  }

  handleOffline() {
    this.sendEvent("connection_offline", null, { status: "offline" });
    if (typeof this.onWarning === "function") {
      this.onWarning("Network connection lost. Reconnecting in background...");
    }
    if (typeof this.onStatusChange === "function") {
      this.onStatusChange({ online: false });
    }
  }

  handleOnline() {
    this.sendEvent("connection_online", null, { status: "online" });
    if (typeof this.onStatusChange === "function") {
      this.onStatusChange({ online: true });
    }
  }

  async startScreenShare(onEnded) {
    if (!navigator.mediaDevices?.getDisplayMedia) {
      throw new Error("Screen sharing is not supported by your browser");
    }
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { cursor: "always" },
        audio: false,
      });
      this.screenStream = stream;
      this.sendEvent("screenshare_started", null, {});

      const track = stream.getVideoTracks()[0];
      if (track) {
        track.onended = () => {
          this.stopScreenShare();
          this.sendEvent("screenshare_stopped", null, { reason: "user_stopped" });
          if (typeof onEnded === "function") onEnded();
        };
      }
      if (typeof this.onStatusChange === "function") {
        this.onStatusChange({ screenSharing: true });
      }
      return stream;
    } catch (err) {
      console.warn("[Proctoring] Screen share request cancelled or denied:", err);
      throw err;
    }
  }

  stopScreenShare() {
    if (this.screenStream) {
      this.screenStream.getTracks().forEach((track) => track.stop());
      this.screenStream = null;
      if (typeof this.onStatusChange === "function") {
        this.onStatusChange({ screenSharing: false });
      }
    }
  }
}

export const proctoringController = new ProctoringController();
export default proctoringController;
