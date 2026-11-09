import { act, createElement, useEffect } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { useHistory } from "./useHistory";

let root, container, result;
function Probe({ filters }) {
  const value = useHistory(filters);
  useEffect(() => { result = value; }, [value]);
  return null;
}
function response(data) { return { ok: true, text: async () => JSON.stringify(data) }; }
async function render(filters = {}) {
  await act(async () => { root.render(createElement(Probe, { filters })); });
}
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

test("poll replaces current aggregate bucket without duplicates", async () => {
  const fetch = vi.fn().mockResolvedValueOnce(response([{ time: "2026-01-01T00:00:00Z", co2: 600 }]))
    .mockResolvedValueOnce(response([{ time: "2026-01-01T00:00:00Z", co2: 650 }]));
  vi.stubGlobal("fetch", fetch);
  await render({ mode: "minute" });
  expect(result.data[0].co2).toBe(600);
  await act(async () => vi.advanceTimersByTimeAsync(10000));
  expect(result.data).toHaveLength(1);
  expect(result.data[0].co2).toBe(650);
});

test("filter changes abort old requests and ignore late responses", async () => {
  let finishOld;
  const fetch = vi.fn().mockImplementationOnce(() => new Promise((resolve) => { finishOld = resolve; }))
    .mockResolvedValueOnce(response([{ co2: 700 }]));
  vi.stubGlobal("fetch", fetch);
  await render({ mode: "minute" });
  const signal = fetch.mock.calls[0][1].signal;
  await render({ mode: "hour" });
  expect(signal.aborted).toBe(true);
  expect(result.data[0].co2).toBe(700);
  await act(async () => finishOld(response([{ co2: 100 }])));
  expect(result.data[0].co2).toBe(700);
});

test("pending requests never overlap", async () => {
  const fetch = vi.fn(() => new Promise(() => {}));
  vi.stubGlobal("fetch", fetch);
  await render();
  await act(async () => vi.advanceTimersByTimeAsync(40000));
  expect(fetch).toHaveBeenCalledTimes(1);
});

test("errors preserve last successful chart", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(response([{ co2: 600 }]))
    .mockRejectedValueOnce(new Error("Network unavailable")));
  await render();
  await act(async () => vi.advanceTimersByTimeAsync(10000));
  expect(result.data[0].co2).toBe(600);
  expect(result.error).toBe("Network unavailable");
});
