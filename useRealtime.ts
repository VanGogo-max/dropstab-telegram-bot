// frontend/src/hooks/useRealtime.ts
/**
 * useRealtime - Интелигентен real-time hook с fallback
 * 
 * STRATEGY:
 * 1. WebSocket (най-добър) → ако не работи →
 * 2. Server-Sent Events (SSE) → ако не работи →
 * 3. Polling с exponential backoff (последна опция)
 * 
 * ЩО ПРАВИ:
 * - Автоматично избира най-добрият метод
 * - Graceful degradation при проблеми
 * - Retry logic за всеки метод
 * 
 * ИЗПОЛЗВАНЕ:
 * const { status, data } = useRealtime('/api/bots/status', {
 *   preferredMethod: 'websocket',
 *   pollingInterval: 5000,
 * });
 */

import { useEffect, useState, useRef, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';
import { apiFetch } from '../utils/apiClient';

type RealtimeMethod = 'websocket' | 'sse' | 'polling';

interface UseRealtimeOptions {
  preferredMethod?: RealtimeMethod;
  pollingInterval?: number;
  maxPollingInterval?: number;
  onData?: (data: any) => void;
  onError?: (error: Error) => void;
}

interface UseRealtimeReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  method: RealtimeMethod;
  connected: boolean;
}

/**
 * useRealtime Hook
 * 
 * @param url - API endpoint (напр. '/api/bots/status')
 * @param options - Настройки
 */
export function useRealtime<T = any>(
  url: string,
  options: UseRealtimeOptions = {}
): UseRealtimeReturn<T> {
  const {
    preferredMethod = 'websocket',
    pollingInterval = 5000,
    maxPollingInterval = 30000,
    onData,
    onError,
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [currentMethod, setCurrentMethod] = useState<RealtimeMethod>(preferredMethod);
  const [connected, setConnected] = useState(false);

  const pollingIntervalRef = useRef<NodeJS.Timeout>();
  const currentDelayRef = useRef(pollingInterval);
  const mountedRef = useRef(true);
  const sseRef = useRef<EventSource | null>(null);

  /**
   * Обработва получени данни
   */
  const handleData = useCallback((newData: any) => {
    setData(newData);
    setLoading(false);
    setError(null);
    onData?.(newData);
  }, [onData]);

  /**
   * Обработва грешки
   */
  const handleError = useCallback((err: Error) => {
    console.error(`[Realtime] Грешка (${currentMethod}):`, err);
    setError(err);
    setLoading(false);
    onError?.(err);
  }, [currentMethod, onError]);

  /**
   * МЕТОД 1: WebSocket
   */
  const { connected: wsConnected } = useWebSocket(
    `/ws${url}`, // WebSocket endpoint
    handleData,
    {
      onOpen: () => {
        console.log('[Realtime] WebSocket свързан');
        setConnected(true);
        setCurrentMethod('websocket');
      },
      onClose: () => {
        console.log('[Realtime] WebSocket изключен, fallback към SSE');
        setConnected(false);
        
        // Превключи към SSE
        if (currentMethod === 'websocket') {
          setCurrentMethod('sse');
        }
      },
      onError: (err) => {
        console.warn('[Realtime] WebSocket грешка, fallback към SSE');
        setCurrentMethod('sse');
      },
    }
  );

  /**
   * МЕТОД 2: Server-Sent Events (SSE)
   */
  const setupSSE = useCallback(() => {
    if (currentMethod !== 'sse' || !mountedRef.current) return;

    console.log('[Realtime] Опит за SSE...');

    try {
      // SSE endpoint (backend трябва да го поддържа)
      const sseUrl = `${url}/stream`;
      const eventSource = new EventSource(sseUrl, { withCredentials: true });
      sseRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('[Realtime] SSE свързан');
        setConnected(true);
        setError(null);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleData(data);
        } catch (err) {
          console.error('[Realtime] SSE parse грешка:', err);
        }
      };

      eventSource.onerror = (err) => {
        console.warn('[Realtime] SSE грешка, fallback към polling');
        eventSource.close();
        sseRef.current = null;
        setConnected(false);
        
        // Превключи към polling
        if (mountedRef.current) {
          setCurrentMethod('polling');
        }
      };

    } catch (err) {
      console.error('[Realtime] SSE setup грешка:', err);
      setCurrentMethod('polling');
    }
  }, [currentMethod, url, handleData]);

  /**
   * МЕТОД 3: Polling с exponential backoff
   */
  const setupPolling = useCallback(() => {
    if (currentMethod !== 'polling' || !mountedRef.current) return;

    console.log('[Realtime] Използване на polling...');

    const poll = async () => {
      if (!mountedRef.current) return;

      try {
        const response = await apiFetch(url, { 
          method: 'GET',
          timeoutMs: 10000,
        });

        if (!response.ok) {
          throw new Error(`Polling failed: ${response.statusText}`);
        }

        const newData = await response.json();
        handleData(newData);
        
        // Success → reset backoff
        currentDelayRef.current = pollingInterval;
        setConnected(true);
        setError(null);

      } catch (err) {
        handleError(err as Error);
        
        // Increase backoff
        currentDelayRef.current = Math.min(
          currentDelayRef.current * 1.5,
          maxPollingInterval
        );
      }

      // Schedule next poll
      if (mountedRef.current) {
        pollingIntervalRef.current = setTimeout(poll, currentDelayRef.current);
      }
    };

    // Start polling
    poll();

  }, [currentMethod, url, pollingInterval, maxPollingInterval, handleData, handleError]);

  /**
   * Cleanup при unmount
   */
  useEffect(() => {
    return () => {
      mountedRef.current = false;
      
      // Cleanup polling
      if (pollingIntervalRef.current) {
        clearTimeout(pollingIntervalRef.current);
      }
      
      // Cleanup SSE
      if (sseRef.current) {
        sseRef.current.close();
        sseRef.current = null;
      }
    };
  }, []);

  /**
   * Setup based on current method
   */
  useEffect(() => {
    if (currentMethod === 'sse') {
      setupSSE();
    } else if (currentMethod === 'polling') {
      setupPolling();
    }
    // WebSocket се setup-ва автоматично от useWebSocket hook
  }, [currentMethod, setupSSE, setupPolling]);

  return {
    data,
    loading,
    error,
    method: currentMethod,
    connected: currentMethod === 'websocket' ? wsConnected : connected,
  };
}

export default useRealtime;
