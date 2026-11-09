import { useEffect, useState } from "react";
import { request } from "../api/client";
import { historyPath } from "../api/history";

export function useHistory(filters) {
  const path = historyPath(filters);
  const [state, setState] = useState(null);
  useEffect(() => {
    const controller = new AbortController();
    let timer;
    async function load() {
      try {
        const data = await request(path, { signal: controller.signal });
        if (!Array.isArray(data)) throw new Error("Invalid history response");
        if (!controller.signal.aborted) setState({ data, error: null });
      } catch (error) {
        if (!controller.signal.aborted) {
          setState((previous) => ({ data: previous?.data ?? [], error: error.message }));
        }
      } finally {
        // Schedule after completion, so requests can never overlap.
        if (!controller.signal.aborted) timer = setTimeout(load, 10000);
      }
    }
    load();
    return () => { controller.abort(); clearTimeout(timer); };
  }, [path]);
  return { data: state?.data ?? [], error: state?.error, loading: state === null };
}
