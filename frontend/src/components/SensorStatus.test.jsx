import { act, createElement } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import SensorStatus from "./SensorStatus";

let root, container;
const response = (snapshot) => ({ ok: true, text: async () => JSON.stringify(snapshot) });
beforeEach(() => {
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  vi.useFakeTimers();
  container = document.createElement("div");
  document.body.append(container);
  root = createRoot(container);
});
afterEach(async () => {
  await act(async () => root.unmount());
  container.remove();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
async function render() { await act(async () => root.render(createElement(SensorStatus))); }

test("shows waiting before the first measurement", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ online: false, last_received_at: null,
    age_seconds: null, stale_after_seconds: 60 })));
  await render();
  expect(container.textContent).toContain("Waiting for measurements");
});

test("freshness expires even before the next poll", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ online: true,
    last_received_at: "2026-01-01T00:00:00Z", age_seconds: 58, stale_after_seconds: 60 })));
  await render();
  expect(container.textContent).toContain("Receiving measurements");
  await act(async () => vi.advanceTimersByTimeAsync(3000));
  expect(container.textContent).toContain("Sensor offline");
});

test("does not present cached status as online after a request failure", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(response({ online: true,
    last_received_at: "2026-01-01T00:00:00Z", age_seconds: 0, stale_after_seconds: 60 }))
    .mockRejectedValueOnce(new Error("Network unavailable")));
  await render();
  await act(async () => vi.advanceTimersByTimeAsync(10000));
  expect(container.textContent).toContain("Sensor status unavailable");
  expect(container.textContent).toContain("Last measurement:");
});
