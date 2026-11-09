import { act, createElement } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, expect, test, vi } from "vitest";
import App from "./App";

vi.mock("./pages/Dashboard", () => ({ default: () => <main><h1>Environmental Metrics</h1></main> }));
let root, container;
afterEach(async () => {
  if (root) await act(async () => root.unmount());
  container?.remove();
  window.history.replaceState({}, "", "/");
});

async function render(path) {
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  window.history.replaceState({}, "", path);
  container = document.createElement("div");
  document.body.append(container);
  root = createRoot(container);
  await act(async () => root.render(createElement(App)));
}

test("opens metrics directly at the root without a login form", async () => {
  await render("/");
  expect(container.textContent).toContain("Environmental Metrics");
  expect(container.querySelector('input[type="password"]')).toBeNull();
});

test("old login links lead to the main metrics page", async () => {
  await render("/admin/login");
  expect(window.location.pathname).toBe("/");
  expect(container.textContent).toContain("Environmental Metrics");
});
