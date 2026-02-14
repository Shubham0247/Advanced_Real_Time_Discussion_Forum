import { useEffect, useRef, useCallback } from "react";

/**
 * Generic WebSocket hook with auto-reconnect.
 *
 * @param {string|null} url  - WebSocket URL (null to disable)
 * @param {(data: object) => void} onMessage - callback for each parsed JSON message
 * @param {object} [options]
 * @param {number} [options.reconnectInterval=3000]
 * @param {number} [options.maxRetries=10]
 */
export default function useWebSocket(url, onMessage, options = {}) {
  const { reconnectInterval = 3000, maxRetries = 10 } = options;
  const wsRef = useRef(null);
  const retriesRef = useRef(0);
  const onMessageRef = useRef(onMessage);
  onMessageRef.current = onMessage;

  const connect = useCallback(() => {
    if (!url) return;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      retriesRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessageRef.current(data);
      } catch {
        // non-JSON message, ignore
      }
    };

    ws.onclose = () => {
      if (retriesRef.current < maxRetries) {
        retriesRef.current += 1;
        setTimeout(connect, reconnectInterval);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [url, reconnectInterval, maxRetries]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null; // prevent reconnect on intentional close
        wsRef.current.close();
      }
    };
  }, [connect]);

  return wsRef;
}
