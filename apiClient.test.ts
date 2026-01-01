// frontend/src/utils/__tests__/apiClient.test.ts
/**
 * Unit Tests за apiClient
 * 
 * ТЕСТВА:
 * - ✅ 401 → automatic refresh → retry
 * - ✅ Timeout handling
 * - ✅ Network errors
 * - ✅ Successful requests
 * - ✅ Skip refresh при вече failed refresh
 * 
 * RUN TESTS:
 * npm test apiClient.test.ts
 * или
 * npm run test:watch
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { apiFetch, apiGet, apiPost } from '../apiClient';

// Mock global fetch
global.fetch = vi.fn();

describe('apiClient', () => {
  beforeEach(() => {
    // Reset mocks преди всеки тест
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  /**
   * TEST 1: Успешна заявка
   */
  it('успешна GET заявка връща данни', async () => {
    const mockData = { bots: [{ id: '1', name: 'Grid Bot' }] };
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    const response = await apiFetch('/api/bots', { method: 'GET' });
    const data = await response.json();

    expect(data).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/bots',
      expect.objectContaining({
        method: 'GET',
        credentials: 'include',
      })
    );
  });

  /**
   * TEST 2: 401 → refresh → retry → success
   */
  it('автоматичен retry след 401 с refresh', async () => {
    const mockData = { bots: [] };

    // Mock fetch responses:
    // 1st call: 401 (unauthorized)
    // 2nd call: 200 (refresh успешен)
    // 3rd call: 200 (retry оригинална заявка успешен)
    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
      });

    const response = await apiFetch('/api/bots', { method: 'GET' });
    const data = await response.json();

    expect(data).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledTimes(3);
    
    // Провери че refresh е извикан
    expect(global.fetch).toHaveBeenNthCalledWith(
      2,
      '/api/auth/refresh',
      expect.objectContaining({
        method: 'POST',
      })
    );
  });

  /**
   * TEST 3: 401 → refresh fail → throw error
   */
  it('хвърля грешка когато refresh fail-не', async () => {
    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Refresh failed',
      });

    await expect(
      apiFetch('/api/bots', { method: 'GET' })
    ).rejects.toThrow('Unauthorized');

    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  /**
   * TEST 4: Timeout handling
   */
  it('хвърля timeout error след 15s', async () => {
    (global.fetch as any).mockImplementation(() => {
      return new Promise((resolve) => {
        // Never resolves (симулира infinite request)
      });
    });

    const promise = apiFetch('/api/slow-endpoint', { timeoutMs: 1000 });

    // Fast-forward time
    vi.advanceTimersByTime(1001);

    await expect(promise).rejects.toThrow('timeout');
  });

  /**
   * TEST 5: Network error
   */
  it('хвърля грешка при network failure', async () => {
    (global.fetch as any).mockRejectedValueOnce(
      new Error('Network error')
    );

    await expect(
      apiFetch('/api/bots', { method: 'GET' })
    ).rejects.toThrow('Network error');
  });

  /**
   * TEST 6: Skip retry при skipRefresh=true
   */
  it('не прави retry при skipRefresh=true', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    const response = await apiFetch('/api/auth/login', {
      method: 'POST',
      skipRefresh: true,
    });

    expect(response.status).toBe(401);
    expect(global.fetch).toHaveBeenCalledTimes(1); // No retry
  });

  /**
   * TEST 7: apiGet helper
   */
  it('apiGet wrapper работи правилно', async () => {
    const mockData = { user: { id: '1', email: 'test@test.com' } };
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    const data = await apiGet('/api/auth/me');

    expect(data).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/me',
      expect.objectContaining({
        method: 'GET',
      })
    );
  });

  /**
   * TEST 8: apiPost helper
   */
  it('apiPost изпраща JSON body', async () => {
    const requestBody = { email: 'test@test.com', password: 'pass123' };
    const mockResponse = { user: { id: '1' }, token: 'abc123' };
    
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockResponse,
    });

    const data = await apiPost('/api/auth/login', requestBody);

    expect(data).toEqual(mockResponse);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
        body: JSON.stringify(requestBody),
      })
    );
  });

  /**
   * TEST 9: Credentials always included
   */
  it('винаги изпраща credentials: include', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({}),
    });

    await apiFetch('/api/test');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        credentials: 'include',
      })
    );
  });

  /**
   * TEST 10: Multiple 401s не правят infinite loop
   */
  it('не прави infinite retry loop', async () => {
    // Mock все 401s
    (global.fetch as any).mockResolvedValue({
      ok: false,
      status: 401,
    });

    await expect(
      apiFetch('/api/bots', { method: 'GET' })
    ).rejects.toThrow();

    // Трябва да има max 2 calls (original + refresh)
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });
});

/**
 * Integration tests (опционално - за CI)
 */
describe('apiClient integration', () => {
  it.skip('real request към test server', async () => {
    // Този тест се пуска само в CI environment
    // с real test backend
    const response = await apiFetch('http://localhost:8000/health');
    expect(response.ok).toBe(true);
  });
});
