/**
 * Custom Hook for Polling
 * Reusable polling logic for real-time updates
 */
import { useEffect, useRef } from 'react';

export const usePolling = (callback, interval = 3000, enabled = true) => {
  const savedCallback = useRef();

  // Remember the latest callback
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  // Set up the interval
  useEffect(() => {
    if (!enabled) return;

    const tick = () => {
      savedCallback.current();
    };

    // Call immediately on mount
    tick();

    const id = setInterval(tick, interval);
    return () => clearInterval(id);
  }, [interval, enabled]);
};
