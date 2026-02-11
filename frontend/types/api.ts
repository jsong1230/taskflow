// ─── Enums ──────────────────────────────────────────────

export type TaskStatus = "todo" | "in_progress" | "done";
export type TaskPriority = "low" | "medium" | "high" | "critical";
export type ProjectRole = "owner" | "admin" | "member";

// ─── Auth ───────────────────────────────────────────────

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginResponse {
  user: User;
  token: Token;
}

// ─── User ───────────────────────────────────────────────

export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

// ─── Project ────────────────────────────────────────────

export interface Project {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  created_at: string;
}

export interface ProjectMember {
  id: number;
  user_id: number;
  project_id: number;
  role: ProjectRole;
}

export interface ProjectDetail extends Project {
  members: ProjectMember[];
}

export interface ProjectCreate {
  name: string;
  description?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
}

export interface ProjectMemberAdd {
  user_id: number;
  role?: ProjectRole;
}

// ─── Task ───────────────────────────────────────────────

export interface Task {
  id: number;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  project_id: number;
  assignee_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  assignee_id?: number | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number | null;
}

export interface TaskStatusUpdate {
  status: TaskStatus;
}

// ─── Comment ────────────────────────────────────────────

export interface Comment {
  id: number;
  content: string;
  task_id: number;
  author_id: number;
  created_at: string;
}

export interface CommentCreate {
  content: string;
}

// ─── Task 필터/정렬 쿼리 파라미터 ──────────────────────

export interface TaskListParams {
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number;
  sort_by?: "created_at" | "updated_at" | "title" | "priority" | "status";
  sort_order?: "asc" | "desc";
}
