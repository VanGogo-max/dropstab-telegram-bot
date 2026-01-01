// frontend/src/utils/apiClient.ts
/**
 * apiClient - Централизиран wrapper за всички API заявки
 * 
 * ЩО ПРАВИ:
 * - Автоматичен retry при 401 (изтекъл токен)
 * - Timeout protection (15s default)
 * - AbortController за cancellation
 * - Автоматично credentials: 'include' за cookies
 * - Error handling и logging
 * 
 * ИЗПОЛЗВАНЕ:
 * const data = await apiFetch('/api/bots', { method: 'GET' });
 * const result = await apiFetch('/api/bots/start', { method: 'POST', body: {...} });
 */

// Типове за options
interface ApiOptions extends RequestInit {
  retry?: boolean;        // Дали да прави retry при 401 (default: true)
  timeoutMs?: number;     // Timeout в milliseconds (default: 15000)
  skipRefresh?: boolean;  // Skip refresh token logic (за /api/auth/refresh самия)
}

/**
 * timeoutFetch - Fetch с timeout защита
 * 
 * Ако заявката не се изпълни в рамките на timeoutMs,
 * автоматично я прекъсва (abort).
 */
async function timeoutFetch(
  input: RequestInfo,
  init?: RequestInit,
  timeoutMs = 15000
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
    console.warn(`[API] Timeout за ${input} след ${timeoutMs}ms`);
  }, timeoutMs);

  try {
    const response = await fetch(input, {
      ...init,
      signal: controller.signal,
      credentials: 'include', // ВАЖНО: изпраща httpOnly cookies
    });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * apiFetch - Главната функция за API calls
 * 
 * FLOW:
 * 1. Прави заявката с timeout
 * 2. Ако е 401 и retry=true → опитва /api/auth/refresh
 * 3. Ако refresh успее → retry оригиналната заявка
 * 4. Ако refresh fail → хвърля Unauthorized error
 */
export async function apiFetch<T = any>(
  input: string,
  options: ApiOptions = {}
): Promise<Response> {
  const {
    retry = true,
    timeoutMs = 15000,
    skipRefresh = false,
    ...init
  } = options;

  try {
    // Първи опит
    console.log(`[API] ${init.method || 'GET'} ${input}`);
    let response = await timeoutFetch(input, init, timeoutMs);

    // Ако е 401 и можем да правим retry
    if (response.status === 401 && retry && !skipRefresh) {
      console.log(`[API] 401 за ${input}, опитвам refresh...`);

      try {
        // Опит за refresh
        const refreshResponse = await timeoutFetch(
          '/api/auth/refresh',
          {
            method: 'POST',
            credentials: 'include',
          },
          timeoutMs
        );

        if (refreshResponse.ok) {
          console.log('[API] Refresh успешен, retry оригинална заявка');
          
          // Retry оригиналната заявка
          response = await timeoutFetch(input, init, timeoutMs);
        } else {
          console.error('[API] Refresh неуспешен');
          throw new Error('Unauthorized - session expired');
        }
      } catch (refreshError) {
        console.error('[API] Refresh грешка:', refreshError);
        throw new Error('Unauthorized - refresh failed');
      }
    }

    // Логваме резултата
    if (!response.ok) {
      console.warn(`[API] ${response.status} ${response.statusText} за ${input}`);
    }

    return response;

  } catch (error) {
    // Timeout или network error
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        console.error(`[API] Timeout за ${input}`);
        throw new Error(`Request timeout за ${input}`);
      }
      console.error(`[API] Грешка за ${input}:`, error.message);
      throw error;
    }
    throw new Error('Unknown API error');
  }
}

/**
 * Помощни функции за различни HTTP методи
 */

export async function apiGet<T = any>(url: string, options?: ApiOptions): Promise<T> {
  const response = await apiFetch(url, { ...options, method: 'GET' });
  if (!response.ok) {
    throw new Error(`GET ${url} failed: ${response.statusText}`);
  }
  return response.json();
}

export async function apiPost<T = any>(
  url: string,
  body?: any,
  options?: ApiOptions
): Promise<T> {
  const response = await apiFetch(url, {
    ...options,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `POST ${url} failed`);
  }
  
  return response.json();
}

export async function apiPut<T = any>(
  url: string,
  body?: any,
  options?: ApiOptions
): Promise<T> {
  const response = await apiFetch(url, {
    ...options,
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  
  if (!response.ok) {
    throw new Error(`PUT ${url} failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function apiDelete<T = any>(url: string, options?: ApiOptions): Promise<T> {
  const response = await apiFetch(url, { ...options, method: 'DELETE' });
  if (!response.ok) {
    throw new Error(`DELETE ${url} failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Типизиран wrapper за JSON response
 */
export async function apiFetchJson<T = any>(
  url: string,
  options?: ApiOptions
): Promise<T> {
  const response = await apiFetch(url, options);
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `API call failed: ${response.statusText}`);
  }
  
  return response.json();
}

export default apiFetch;
