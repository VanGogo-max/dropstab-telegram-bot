// frontend/src/context/__tests__/AuthProvider.test.tsx
/**
 * Unit Tests за AuthProvider
 * 
 * ТЕСТВА:
 * - ✅ Login flow (успешен и неуспешен)
 * - ✅ Logout
 * - ✅ Session persistence (ensureSession)
 * - ✅ Auto-refresh при 401
 * - ✅ Loading states
 * 
 * RUN TESTS:
 * npm test AuthProvider.test.tsx
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../AuthProvider';
import React from 'react';

// Mock global fetch
global.fetch = vi.fn();

// Wrapper за hooks
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('AuthProvider', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * TEST 1: Initial state
   */
  it('начално състояние е loading=true, user=null', () => {
    // Mock /api/auth/me да fail-не (no session)
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.loading).toBe(true);
    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
  });

  /**
   * TEST 2: ensureSession при валидна сесия
   */
  it('ensureSession зарежда user при валиден cookie', async () => {
    const mockUser = { id: '1', email: 'test@test.com', name: 'Test User' };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ user: mockUser }),
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });

  /**
   * TEST 3: ensureSession с refresh при 401
   */
  it('ensureSession прави refresh при изтекъл токен', async () => {
    const mockUser = { id: '1', email: 'test@test.com', name: 'Test User' };

    // Mock responses:
    // 1. /api/auth/me → 401 (изтекъл токен)
    // 2. /api/auth/refresh → 200 (refresh успешен)
    // 3. /api/auth/me → 200 (retry успешен)
    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ user: mockUser }),
      });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(global.fetch).toHaveBeenCalledTimes(2); // /api/auth/me + /api/auth/refresh
  });

  /**
   * TEST 4: ensureSession fail при неуспешен refresh
   */
  it('ensureSession logout при failed refresh', async () => {
    // Mock responses:
    // 1. /api/auth/me → 401
    // 2. /api/auth/refresh → 401 (refresh също fail)
    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
  });

  /**
   * TEST 5: Login flow - успешен
   */
  it('login сетва user при успешен вход', async () => {
    const mockUser = { id: '1', email: 'test@test.com', name: 'Test User' };

    // Mock initial /api/auth/me (no session)
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Mock login response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ user: mockUser }),
    });

    // Изпълни login
    await act(async () => {
      await result.current.login('test@test.com', 'password123');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify({ email: 'test@test.com', password: 'password123' }),
      })
    );
  });

  /**
   * TEST 6: Login flow - неуспешен
   */
  it('login хвърля error при неуспешен вход', async () => {
    // Mock initial /api/auth/me
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Mock failed login
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
      text: async () => 'Invalid credentials',
    });

    // Изпълни login и очаквай error
    await expect(
      act(async () => {
        await result.current.login('wrong@test.com', 'wrongpass');
      })
    ).rejects.toThrow();

    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
  });

  /**
   * TEST 7: Logout flow
   */
  it('logout изчиства user state', async () => {
    const mockUser = { id: '1', email: 'test@test.com', name: 'Test User' };

    // Mock initial session
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ user: mockUser }),
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser);
    });

    // Mock logout response
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
    });

    // Изпълни logout
    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/logout',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
      })
    );
  });

  /**
   * TEST 8: Loading state management
   */
  it('loading е true по време на async операции', async () => {
    (global.fetch as any).mockImplementation(() => {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            ok: true,
            json: async () => ({ user: { id: '1' } }),
          });
        }, 100);
      });
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });

  /**
   * TEST 9: Multiple concurrent logins
   */
  it('handling на concurrent login calls', async () => {
    const mockUser = { id: '1', email: 'test@test.com', name: 'Test User' };

    // Mock initial state
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 401,
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Mock login success
    (global.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ user: mockUser }),
    });

    // Две concurrent login calls
    await act(async () => {
      await Promise.all([
        result.current.login('test@test.com', 'pass1'),
        result.current.login('test@test.com', 'pass2'),
      ]);
    });

    // Само последният трябва да е активен
    expect(result.current.user).toEqual(mockUser);
  });

  /**
   * TEST 10: Network error handling
   */
  it('handling на network errors', async () => {
    (global.fetch as any).mockRejectedValueOnce(
      new Error('Network failure')
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
  });
});

/**
 * Integration tests с real components
 */
describe('AuthProvider integration', () => {
  it.skip('работи с real React components', () => {
    // Този тест се пуска само когато имаш готови components
    // Пример:
    // render(<App />);
    // const loginButton = screen.getByText('Login');
    // fireEvent.click(loginButton);
  });
});
