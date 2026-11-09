import { useEffect, useState } from "react";
import { request } from "../api/client";

export function useSensorStatus() {
  const [state, setState] = useState({ snapshot: null, error: null, checkedAt: 0 });
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const controller = new AbortController();
    let timer;
    async function load() {
      try {
        const snapshot = await request("/status", { signal: controller.signal });
        if (!snapshot || typeof snapshot.online !== "boolean") throw new Error("Invalid sensor status");
        if (!controller.signal.aborted) setState({ snapshot, error: null, checkedAt: Date.now() });
      } catch (error) {
        if (!controller.signal.aborted) setState((previous) => ({ ...previous, error: error.message }));
      } finally {
        if (!controller.signal.aborted) timer = setTimeout(load, 10000);
      }
    }
    load();
    return () => { controller.abort(); clearTimeout(timer); };
  }, []);
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  const elapsed = Math.max(0, (now - state.checkedAt) / 1000);
  const age = state.snapshot?.age_seconds == null ? null : state.snapshot.age_seconds + elapsed;
  return { snapshot: state.snapshot, error: state.error, age,
    online: age !== null && age <= state.snapshot.stale_after_seconds };
}
