export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = endpoint.startsWith('/') ? `/api/v1${endpoint}` : `/api/v1/${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorData: unknown;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }
    throw new ApiError(
      `API Request Failed: ${response.status} ${response.statusText}`,
      response.status,
      errorData
    );
  }

  return response.json() as Promise<T>;
}
