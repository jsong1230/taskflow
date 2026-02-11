const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── 토큰 관리 ─────────────────────────────────────────

let accessToken: string | null = null;

export function setToken(token: string | null): void {
  accessToken = token;
  if (typeof window !== "undefined") {
    if (token) {
      localStorage.setItem("access_token", token);
    } else {
      localStorage.removeItem("access_token");
    }
  }
}

export function getToken(): string | null {
  if (accessToken) return accessToken;
  if (typeof window !== "undefined") {
    accessToken = localStorage.getItem("access_token");
  }
  return accessToken;
}

// ─── 에러 클래스 ────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ─── 핵심 fetch 래퍼 ───────────────────────────────────

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const token = getToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, { ...options, headers });

  // 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.detail ?? `API error: ${response.status}`, body);
  }

  return response.json() as Promise<T>;
}

// ─── HTTP 메서드 헬퍼 ──────────────────────────────────

function buildQuery(params?: Record<string, unknown>): string {
  if (!params) return "";
  const entries = Object.entries(params).filter(([, v]) => v != null);
  if (entries.length === 0) return "";
  const qs = new URLSearchParams(entries.map(([k, v]) => [k, String(v)]));
  return `?${qs.toString()}`;
}

export const api = {
  get<T>(path: string, params?: Record<string, unknown>): Promise<T> {
    return request<T>(path + buildQuery(params), { method: "GET" });
  },

  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "POST",
      body: body != null ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "PUT",
      body: body != null ? JSON.stringify(body) : undefined,
    });
  },

  patch<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, {
      method: "PATCH",
      body: body != null ? JSON.stringify(body) : undefined,
    });
  },

  delete<T = void>(path: string): Promise<T> {
    return request<T>(path, { method: "DELETE" });
  },
};

// ─── 도메인별 API 함수 ─────────────────────────────────

import type {
  Comment,
  CommentCreate,
  LoginResponse,
  Project,
  ProjectCreate,
  ProjectDetail,
  ProjectMember,
  ProjectMemberAdd,
  ProjectUpdate,
  Task,
  TaskCreate,
  TaskListParams,
  TaskStatusUpdate,
  TaskUpdate,
  User,
} from "@/types/api";

// Auth
export const authApi = {
  register(data: { email: string; name: string; password: string }): Promise<User> {
    return api.post("/api/v1/auth/register", data);
  },
  login(data: { email: string; password: string }): Promise<LoginResponse> {
    return api.post("/api/v1/auth/login", data);
  },
  me(): Promise<User> {
    return api.get("/api/v1/auth/me");
  },
};

// Projects
export const projectApi = {
  create(data: ProjectCreate): Promise<Project> {
    return api.post("/api/v1/projects/", data);
  },
  list(): Promise<Project[]> {
    return api.get("/api/v1/projects/");
  },
  get(projectId: number): Promise<ProjectDetail> {
    return api.get(`/api/v1/projects/${projectId}`);
  },
  update(projectId: number, data: ProjectUpdate): Promise<Project> {
    return api.put(`/api/v1/projects/${projectId}`, data);
  },
  delete(projectId: number): Promise<void> {
    return api.delete(`/api/v1/projects/${projectId}`);
  },
  addMember(projectId: number, data: ProjectMemberAdd): Promise<ProjectMember> {
    return api.post(`/api/v1/projects/${projectId}/members`, data);
  },
};

// Tasks
export const taskApi = {
  create(projectId: number, data: TaskCreate): Promise<Task> {
    return api.post(`/api/v1/projects/${projectId}/tasks`, data);
  },
  list(projectId: number, params?: TaskListParams): Promise<Task[]> {
    return api.get(`/api/v1/projects/${projectId}/tasks`, params as Record<string, unknown>);
  },
  get(projectId: number, taskId: number): Promise<Task> {
    return api.get(`/api/v1/projects/${projectId}/tasks/${taskId}`);
  },
  update(projectId: number, taskId: number, data: TaskUpdate): Promise<Task> {
    return api.put(`/api/v1/projects/${projectId}/tasks/${taskId}`, data);
  },
  updateStatus(projectId: number, taskId: number, data: TaskStatusUpdate): Promise<Task> {
    return api.patch(`/api/v1/projects/${projectId}/tasks/${taskId}/status`, data);
  },
  delete(projectId: number, taskId: number): Promise<void> {
    return api.delete(`/api/v1/projects/${projectId}/tasks/${taskId}`);
  },
};

// Comments
export const commentApi = {
  create(projectId: number, taskId: number, data: CommentCreate): Promise<Comment> {
    return api.post(`/api/v1/projects/${projectId}/tasks/${taskId}/comments`, data);
  },
  list(projectId: number, taskId: number): Promise<Comment[]> {
    return api.get(`/api/v1/projects/${projectId}/tasks/${taskId}/comments`);
  },
};
