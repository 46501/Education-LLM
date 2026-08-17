export class APIError extends Error {
  status: number;
  code: string;

  constructor(message: string, status: number = 500, code: string = "INTERNAL_ERROR") {
    super(message);
    this.status = status;
    this.code = code;
    this.name = "APIError";
  }
}

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  const url = `http://localhost:8000${endpoint}`;

  let response: Response;
  try {
    response = await fetch(url, config);
  } catch (error) {
    throw new APIError("Network error. Please check your connection and try again.", 0, "NETWORK_ERROR");
  }

  if (!response.ok) {
    let errorMessage = "An unexpected error occurred.";
    let errorCode = "UNKNOWN_ERROR";
    try {
      const errorData = await response.json();
      if (errorData.error) {
        errorMessage = errorData.error.message || errorMessage;
        errorCode = errorData.error.code || errorCode;
      } else if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } catch (e) {
      // Failed to parse JSON error, fallback to status text
      errorMessage = response.statusText || errorMessage;
    }

    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
        // Optionally redirect to login here, or let components handle it
      }
    }

    throw new APIError(errorMessage, response.status, errorCode);
  }

  // Handle empty responses
  if (response.status === 204) {
    return {} as T;
  }

  try {
    const data = await response.json();
    return data;
  } catch (e) {
    throw new APIError("Failed to parse server response.", 500, "PARSE_ERROR");
  }
}
