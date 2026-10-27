import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { proctoringController } from "./proctoringController";
import * as careerService from "./careerService";

describe("ProctoringController telemetry & lifecycle", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    proctoringController.stop();
  });

  afterEach(() => {
    proctoringController.stop();
  });

  it("does not send events when unproctored mode is active", async () => {
    const spy = vi.spyOn(careerService, "recordProctoringEvent").mockResolvedValue({});
    proctoringController.start({ sessionId: "sess-123", unproctored: true });

    await proctoringController.sendEvent("visibility_hidden");
    expect(spy).not.toHaveBeenCalled();
  });

  it("records visibility change and debounces rapid duplicates", async () => {
    const spy = vi.spyOn(careerService, "recordProctoringEvent").mockResolvedValue({});
    proctoringController.start({ sessionId: "sess-123", unproctored: false });

    await proctoringController.sendEvent("window_blur");
    expect(spy).toHaveBeenCalledTimes(1);

    // Immediate duplicate within 500ms should be debounced client-side
    await proctoringController.sendEvent("window_blur");
    expect(spy).toHaveBeenCalledTimes(1);
  });

  it("notifies warning callback on visibility change", () => {
    const warningCallback = vi.fn();
    proctoringController.start({
      sessionId: "sess-123",
      onWarning: warningCallback,
    });

    // Simulate tab hidden
    Object.defineProperty(document, "hidden", { value: true, configurable: true });
    proctoringController.handleVisibilityChange();

    expect(warningCallback).toHaveBeenCalledWith(
      expect.stringContaining("Interview window lost visibility")
    );
  });

  it("cleans up listeners and stops upon controller.stop()", () => {
    const statusCallback = vi.fn();
    proctoringController.start({
      sessionId: "sess-123",
      onStatusChange: statusCallback,
    });
    expect(proctoringController.isActive).toBe(true);

    proctoringController.stop();
    expect(proctoringController.isActive).toBe(false);
    expect(proctoringController.sessionId).toBeNull();
  });
});
