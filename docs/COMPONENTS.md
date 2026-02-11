# TaskFlow 컴포넌트 가이드

## 목차
- [개요](#개요)
- [칸반 보드 컴포넌트](#칸반-보드-컴포넌트)
- [대시보드 컴포넌트](#대시보드-컴포넌트)
- [공통 컴포넌트](#공통-컴포넌트)
- [타입 정의](#타입-정의)
- [컴포넌트 간 데이터 흐름](#컴포넌트-간-데이터-흐름)

---

## 개요

TaskFlow의 프론트엔드는 Next.js 15 (App Router)와 TypeScript를 사용하며, 재사용 가능한 컴포넌트로 구성되어 있습니다.

**컴포넌트 디렉토리 구조**

```
frontend/components/
├── kanban/                    # 칸반 보드 관련 컴포넌트
│   ├── KanbanBoard.tsx        # 전체 칸반 보드 (3개 컬럼)
│   ├── KanbanColumn.tsx       # 개별 컬럼 (Todo, In Progress, Done)
│   ├── TaskCard.tsx           # 태스크 카드
│   ├── TaskDetailModal.tsx    # 태스크 상세 모달
│   ├── CreateTaskForm.tsx     # 태스크 생성 폼
│   └── CommentSection.tsx     # 댓글 섹션
├── dashboard/                 # 대시보드 컴포넌트
│   ├── ProjectStatsCard.tsx   # 프로젝트 통계 카드
│   ├── ProgressBar.tsx        # 진행률 바
│   └── AssignedTasksList.tsx  # 내 태스크 목록
└── ProtectedRoute.tsx         # 인증 보호 라우트
```

---

## 칸반 보드 컴포넌트

### 1. KanbanBoard

칸반 보드 전체를 관리하는 메인 컴포넌트입니다. 3개 컬럼 (Todo, In Progress, Done)을 렌더링하고 드래그 앤 드롭 로직을 처리합니다.

**파일 위치**: `components/kanban/KanbanBoard.tsx`

#### Props

```typescript
interface KanbanBoardProps {
  projectId: number;                      // 프로젝트 ID
  onTaskClick: (taskId: number) => void;  // 태스크 클릭 핸들러
  onCreateTask: (status: TaskStatus) => void;  // 태스크 생성 핸들러
}
```

#### 주요 기능

- **태스크 목록 조회**: 컴포넌트 마운트 시 프로젝트의 모든 태스크를 API에서 가져옴
- **드래그 앤 드롭**: HTML5 Drag and Drop API를 사용하여 태스크 상태 변경
- **낙관적 업데이트**: 드래그 시 즉시 UI 업데이트 후 API 요청, 실패 시 롤백

#### 사용 예시

```typescript
// app/projects/[id]/page.tsx
'use client';

import KanbanBoard from '@/components/kanban/KanbanBoard';

export default function ProjectPage({ params }: { params: { id: string } }) {
  const projectId = parseInt(params.id);

  const handleTaskClick = (taskId: number) => {
    setSelectedTaskId(taskId);
    setIsModalOpen(true);
  };

  const handleCreateTask = (status: TaskStatus) => {
    setInitialStatus(status);
    setIsCreateFormOpen(true);
  };

  return (
    <KanbanBoard
      projectId={projectId}
      onTaskClick={handleTaskClick}
      onCreateTask={handleCreateTask}
    />
  );
}
```

#### 드래그 앤 드롭 로직

```typescript
// 드래그 시작
const handleDragStart = (e: React.DragEvent, taskId: number) => {
  setDraggedTaskId(taskId);
  e.dataTransfer.effectAllowed = 'move';
};

// 드래그 오버 (드롭 허용)
const handleDragOver = (e: React.DragEvent) => {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
};

// 드롭 (상태 변경)
const handleDrop = async (e: React.DragEvent, newStatus: TaskStatus) => {
  e.preventDefault();
  if (!draggedTaskId) return;

  const task = tasks.find((t) => t.id === draggedTaskId);
  if (!task || task.status === newStatus) {
    setDraggedTaskId(null);
    return;
  }

  // 낙관적 업데이트
  const previousTasks = [...tasks];
  setTasks((prev) =>
    prev.map((t) => (t.id === draggedTaskId ? { ...t, status: newStatus } : t))
  );

  try {
    await taskApi.updateStatus(projectId, draggedTaskId, { status: newStatus });
  } catch (err) {
    // 롤백
    setTasks(previousTasks);
    alert('태스크 상태 변경에 실패했습니다.');
  } finally {
    setDraggedTaskId(null);
  }
};
```

---

### 2. KanbanColumn

개별 컬럼 (Todo, In Progress, Done)을 렌더링합니다.

**파일 위치**: `components/kanban/KanbanColumn.tsx`

#### Props

```typescript
interface KanbanColumnProps {
  status: TaskStatus;                       // 컬럼 상태 ('todo', 'in_progress', 'done')
  title: string;                            // 컬럼 제목 ('Todo', 'In Progress', 'Done')
  tasks: Task[];                            // 이 컬럼에 속한 태스크 목록
  onDragOver: (e: React.DragEvent) => void; // 드래그 오버 핸들러
  onDrop: (e: React.DragEvent, newStatus: TaskStatus) => void;  // 드롭 핸들러
  onDragStart: (e: React.DragEvent, taskId: number) => void;    // 드래그 시작 핸들러
  onTaskClick: (taskId: number) => void;    // 태스크 클릭 핸들러
  onCreateTask: (status: TaskStatus) => void;  // 태스크 생성 핸들러
}
```

#### 구조

```typescript
<div className="flex flex-col bg-gray-100 rounded-lg p-4 min-h-[600px]">
  {/* 헤더: 컬럼 제목 + 태스크 개수 */}
  <div className="flex items-center justify-between mb-4">
    <h2>{title} ({tasks.length})</h2>
  </div>

  {/* 드롭 영역: 태스크 카드들 */}
  <div onDragOver={onDragOver} onDrop={(e) => onDrop(e, status)}>
    {tasks.map((task) => (
      <TaskCard key={task.id} task={task} ... />
    ))}
  </div>

  {/* 새 태스크 추가 버튼 */}
  <button onClick={() => onCreateTask(status)}>
    + 태스크 추가
  </button>
</div>
```

---

### 3. TaskCard

개별 태스크 카드를 렌더링합니다. 드래그 가능합니다.

**파일 위치**: `components/kanban/TaskCard.tsx`

#### Props

```typescript
interface TaskCardProps {
  task: Task;                                    // 태스크 데이터
  onDragStart: (e: React.DragEvent, taskId: number) => void;  // 드래그 시작 핸들러
  onClick: (taskId: number) => void;             // 클릭 핸들러
}
```

#### 표시 정보

- **제목**: 최대 2줄 (line-clamp-2)
- **설명**: 최대 2줄 (설명이 있는 경우에만 표시)
- **우선순위 뱃지**: 색상으로 구분
  - `low`: 회색
  - `medium`: 파란색
  - `high`: 주황색
  - `critical`: 빨간색
- **담당자 아바타**: 담당자가 있는 경우 표시 (간단한 숫자 아바타)

#### 스타일링

```typescript
const PRIORITY_CONFIG: Record<TaskPriority, { label: string; color: string; bgColor: string }> = {
  low: { label: '낮음', color: 'text-gray-700', bgColor: 'bg-gray-100' },
  medium: { label: '보통', color: 'text-blue-700', bgColor: 'bg-blue-100' },
  high: { label: '높음', color: 'text-orange-700', bgColor: 'bg-orange-100' },
  critical: { label: '긴급', color: 'text-red-700', bgColor: 'bg-red-100' },
};
```

#### 사용 예시

```typescript
<TaskCard
  task={task}
  onDragStart={handleDragStart}
  onClick={handleTaskClick}
/>
```

---

### 4. TaskDetailModal

태스크 상세 정보를 보여주고 수정/삭제할 수 있는 모달입니다.

**파일 위치**: `components/kanban/TaskDetailModal.tsx`

#### Props

```typescript
interface TaskDetailModalProps {
  projectId: number;        // 프로젝트 ID
  taskId: number;           // 태스크 ID
  onClose: () => void;      // 모달 닫기 핸들러
  onUpdate: () => void;     // 태스크 수정 후 콜백 (칸반 보드 새로고침)
  onDelete: () => void;     // 태스크 삭제 후 콜백
}
```

#### 주요 기능

- **태스크 정보 조회**: 모달 열릴 때 API에서 태스크 데이터 가져오기
- **인라인 수정**: 제목, 설명, 상태, 우선순위 변경 즉시 API 요청
- **댓글 섹션**: CommentSection 컴포넌트 포함
- **삭제**: 확인 후 태스크 삭제

#### 수정 로직

```typescript
const handleUpdateField = async (updates: Partial<Task>) => {
  if (!task) return;

  // 낙관적 업데이트
  const previousTask = { ...task };
  setTask({ ...task, ...updates });

  try {
    await taskApi.update(projectId, taskId, updates);
    onUpdate();  // 부모 컴포넌트에 알림 (칸반 보드 새로고침)
  } catch (err) {
    // 롤백
    setTask(previousTask);
    alert('태스크 수정에 실패했습니다.');
  }
};
```

#### 사용 예시

```typescript
{isModalOpen && selectedTaskId && (
  <TaskDetailModal
    projectId={projectId}
    taskId={selectedTaskId}
    onClose={() => setIsModalOpen(false)}
    onUpdate={refreshTasks}
    onDelete={refreshTasks}
  />
)}
```

---

### 5. CreateTaskForm

새 태스크를 생성하는 모달 폼입니다.

**파일 위치**: `components/kanban/CreateTaskForm.tsx`

#### Props

```typescript
interface CreateTaskFormProps {
  projectId: number;            // 프로젝트 ID
  initialStatus: TaskStatus;    // 초기 상태 (태스크 생성 후 이 컬럼에 추가)
  onClose: () => void;          // 모달 닫기 핸들러
  onSuccess: () => void;        // 생성 성공 후 콜백 (칸반 보드 새로고침)
}
```

#### 입력 필드

- **제목** (필수): 1-300자
- **설명** (선택): 최대 5000자
- **우선순위** (선택): low, medium, high, critical (기본값: medium)

#### 생성 로직

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!title.trim()) return;

  setIsSubmitting(true);
  try {
    // 1. 태스크 생성 (기본 상태는 'todo')
    const newTask = await taskApi.create(projectId, {
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
    });

    // 2. 초기 상태가 'todo'가 아니면 상태 업데이트
    if (initialStatus !== 'todo') {
      await taskApi.updateStatus(projectId, newTask.id, { status: initialStatus });
    }

    onSuccess();  // 칸반 보드 새로고침
    onClose();
  } catch (err) {
    console.error('Failed to create task:', err);
    alert('태스크 생성에 실패했습니다.');
  } finally {
    setIsSubmitting(false);
  }
};
```

#### 사용 예시

```typescript
{isCreateFormOpen && (
  <CreateTaskForm
    projectId={projectId}
    initialStatus={initialStatus}
    onClose={() => setIsCreateFormOpen(false)}
    onSuccess={refreshTasks}
  />
)}
```

---

### 6. CommentSection

태스크의 댓글을 표시하고 작성할 수 있는 섹션입니다.

**파일 위치**: `components/kanban/CommentSection.tsx`

#### Props

```typescript
interface CommentSectionProps {
  projectId: number;  // 프로젝트 ID
  taskId: number;     // 태스크 ID
}
```

#### 주요 기능

- **댓글 목록 조회**: 컴포넌트 마운트 시 댓글 가져오기
- **댓글 작성**: 폼 제출 시 API 요청 및 목록 업데이트
- **스크롤 가능한 목록**: 최대 높이 제한 (max-h-60)

#### 댓글 작성 로직

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!newComment.trim()) return;

  setIsSubmitting(true);
  try {
    const comment = await commentApi.create(projectId, taskId, {
      content: newComment.trim(),
    });
    setComments([...comments, comment]);  // 목록에 추가
    setNewComment('');  // 입력 필드 초기화
  } catch (err) {
    console.error('Failed to create comment:', err);
    alert('댓글 작성에 실패했습니다.');
  } finally {
    setIsSubmitting(false);
  }
};
```

#### UI 구조

```typescript
<div>
  <h3>댓글 ({comments.length})</h3>

  {/* 댓글 목록 */}
  <div className="space-y-3 max-h-60 overflow-y-auto">
    {comments.map((comment) => (
      <div key={comment.id} className="bg-gray-50 rounded-lg p-3">
        <div className="flex items-start justify-between mb-2">
          <div>아바타 + 작성자</div>
          <span>작성일</span>
        </div>
        <p>{comment.content}</p>
      </div>
    ))}
  </div>

  {/* 댓글 작성 폼 */}
  <form onSubmit={handleSubmit}>
    <textarea placeholder="댓글을 입력하세요..." />
    <button type="submit">댓글 작성</button>
  </form>
</div>
```

---

## 대시보드 컴포넌트

### 1. ProjectStatsCard

프로젝트의 통계를 보여주는 카드입니다. 클릭하면 칸반 보드로 이동합니다.

**파일 위치**: `components/dashboard/ProjectStatsCard.tsx`

#### Props

```typescript
interface ProjectStatsCardProps {
  project: Project;  // 프로젝트 데이터
  tasks: Task[];     // 프로젝트의 모든 태스크
}
```

#### 표시 정보

- **프로젝트 이름**
- **프로젝트 설명** (최대 2줄)
- **진행률 바** (완료된 태스크 / 전체 태스크)
- **상태별 태스크 수** (Todo, In Progress, Done)

#### 계산 로직

```typescript
const todoCount = tasks.filter((t) => t.status === 'todo').length;
const inProgressCount = tasks.filter((t) => t.status === 'in_progress').length;
const doneCount = tasks.filter((t) => t.status === 'done').length;
const totalCount = tasks.length;

const progressPercent = totalCount === 0 ? 0 : Math.round((doneCount / totalCount) * 100);
```

#### 사용 예시

```typescript
// app/dashboard/page.tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {projects.map((project) => {
    const projectTasks = allTasks.filter((t) => t.project_id === project.id);
    return (
      <ProjectStatsCard
        key={project.id}
        project={project}
        tasks={projectTasks}
      />
    );
  })}
</div>
```

---

### 2. ProgressBar

진행률을 시각화하는 바 컴포넌트입니다.

**파일 위치**: `components/dashboard/ProgressBar.tsx`

#### Props

```typescript
interface ProgressBarProps {
  total: number;        // 전체 항목 수
  completed: number;    // 완료된 항목 수
  showLabel?: boolean;  // 라벨 표시 여부 (기본값: true)
}
```

#### UI 구조

```typescript
<div>
  {/* 진행률 바 */}
  <div className="w-full bg-gray-200 rounded-full h-2">
    <div
      className="bg-green-600 h-2 rounded-full transition-all duration-300"
      style={{ width: `${progressPercent}%` }}
    />
  </div>

  {/* 라벨 (선택사항) */}
  {showLabel && (
    <div className="flex justify-between text-xs text-gray-600 mt-1">
      <span>{completed}/{total}</span>
      <span>{progressPercent}%</span>
    </div>
  )}
</div>
```

#### 사용 예시

```typescript
// 라벨 포함
<ProgressBar total={20} completed={15} />

// 라벨 없음
<ProgressBar total={20} completed={15} showLabel={false} />
```

---

### 3. AssignedTasksList

현재 사용자에게 배정된 태스크 목록을 보여줍니다.

**파일 위치**: `components/dashboard/AssignedTasksList.tsx`

#### Props

```typescript
interface AssignedTasksListProps {
  tasks: Task[];  // 배정된 태스크 목록
}
```

#### 표시 정보

- 최대 5개 태스크 표시
- 각 태스크: 제목, 프로젝트명, 우선순위, 상태

#### 필터링 로직

```typescript
// 부모 컴포넌트에서 필터링
const assignedTasks = allTasks.filter((t) => t.assignee_id === currentUser.id);
```

#### 사용 예시

```typescript
// app/dashboard/page.tsx
<AssignedTasksList tasks={assignedTasks} />
```

---

## 공통 컴포넌트

### ProtectedRoute

인증된 사용자만 접근할 수 있는 라우트를 보호합니다.

**파일 위치**: `components/ProtectedRoute.tsx`

#### Props

```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;  // 보호할 페이지 컨텐츠
}
```

#### 동작 방식

1. AuthContext에서 현재 사용자 확인
2. 로딩 중이면 "로딩 중..." 표시
3. 사용자가 없으면 `/login`으로 리다이렉트
4. 사용자가 있으면 children 렌더링

#### 사용 예시

```typescript
// app/dashboard/page.tsx
'use client';

import ProtectedRoute from '@/components/ProtectedRoute';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>
        <h1>대시보드</h1>
        {/* ... */}
      </div>
    </ProtectedRoute>
  );
}
```

---

## 타입 정의

**파일 위치**: `types/api.ts`

### Enums

```typescript
export type TaskStatus = "todo" | "in_progress" | "done";
export type TaskPriority = "low" | "medium" | "high" | "critical";
export type ProjectRole = "owner" | "admin" | "member";
```

### User

```typescript
export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}
```

### Project

```typescript
export interface Project {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  created_at: string;
}

export interface ProjectDetail extends Project {
  members: ProjectMember[];
}

export interface ProjectMember {
  id: number;
  user_id: number;
  project_id: number;
  role: ProjectRole;
}
```

### Task

```typescript
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
```

### Comment

```typescript
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
```

---

## 컴포넌트 간 데이터 흐름

### 칸반 보드 플로우

```
ProjectPage (app/projects/[id]/page.tsx)
  ├─ KanbanBoard (전체 보드 관리)
  │   ├─ KanbanColumn (Todo)
  │   │   ├─ TaskCard
  │   │   ├─ TaskCard
  │   │   └─ TaskCard
  │   ├─ KanbanColumn (In Progress)
  │   │   ├─ TaskCard
  │   │   └─ TaskCard
  │   └─ KanbanColumn (Done)
  │       ├─ TaskCard
  │       └─ TaskCard
  │
  ├─ TaskDetailModal (태스크 상세)
  │   └─ CommentSection (댓글)
  │
  └─ CreateTaskForm (태스크 생성)
```

### 데이터 흐름

```
1. 사용자 액션 (드래그 앤 드롭)
   ↓
2. KanbanBoard: handleDrop 실행
   ↓
3. 낙관적 업데이트 (즉시 UI 변경)
   ↓
4. API 요청 (taskApi.updateStatus)
   ↓
5. 성공: UI 유지
   실패: 이전 상태로 롤백
```

### 태스크 수정 플로우

```
1. 사용자가 태스크 카드 클릭
   ↓
2. ProjectPage: setSelectedTaskId(taskId)
   ↓
3. TaskDetailModal 렌더링
   ↓
4. TaskDetailModal: fetchTask() (API 호출)
   ↓
5. 사용자가 제목 수정
   ↓
6. TaskDetailModal: handleUpdateField({ title: '...' })
   ↓
7. API 요청 (taskApi.update)
   ↓
8. ProjectPage: onUpdate() → refreshTasks()
   ↓
9. KanbanBoard 재렌더링 (업데이트된 태스크 반영)
```

---

## 스타일링 가이드

### Tailwind CSS 클래스

TaskFlow는 Tailwind CSS를 사용하여 스타일링합니다.

#### 공통 패턴

**카드**
```typescript
className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200"
```

**버튼 (Primary)**
```typescript
className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
```

**버튼 (Secondary)**
```typescript
className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
```

**입력 필드**
```typescript
className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
```

**모달 오버레이**
```typescript
className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
```

#### 색상 팔레트

| 용도 | 색상 | Tailwind 클래스 |
|------|------|------------------|
| Primary | 파란색 | `bg-blue-600`, `text-blue-600` |
| Success | 초록색 | `bg-green-600`, `text-green-600` |
| Warning | 주황색 | `bg-orange-600`, `text-orange-600` |
| Danger | 빨간색 | `bg-red-600`, `text-red-600` |
| Gray (배경) | 회색 | `bg-gray-100`, `bg-gray-50` |

---

## 컴포넌트 테스트

현재 컴포넌트 테스트는 구현되지 않았습니다. 추후 Jest + React Testing Library를 이용하여 다음과 같은 테스트를 추가할 예정입니다.

### 예시: TaskCard 테스트

```typescript
// components/kanban/__tests__/TaskCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import TaskCard from '../TaskCard';

const mockTask: Task = {
  id: 1,
  title: '테스트 태스크',
  description: '테스트 설명',
  status: 'todo',
  priority: 'high',
  project_id: 1,
  assignee_id: null,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

test('renders task title', () => {
  const onDragStart = jest.fn();
  const onClick = jest.fn();

  render(<TaskCard task={mockTask} onDragStart={onDragStart} onClick={onClick} />);

  expect(screen.getByText('테스트 태스크')).toBeInTheDocument();
});

test('calls onClick when clicked', () => {
  const onDragStart = jest.fn();
  const onClick = jest.fn();

  render(<TaskCard task={mockTask} onDragStart={onDragStart} onClick={onClick} />);

  fireEvent.click(screen.getByText('테스트 태스크'));
  expect(onClick).toHaveBeenCalledWith(1);
});
```

---

## 추가 개선 사항

### 현재 구현되지 않은 컴포넌트

1. **UserAvatar** - 사용자 아바타 (현재는 숫자만 표시)
2. **Notification** - 토스트 알림 (현재는 alert 사용)
3. **Loading** - 로딩 인디케이터 (현재는 "로딩 중..." 텍스트)
4. **ErrorBoundary** - 에러 경계 처리

---

## 참고 자료

- **React 공식 문서**: https://react.dev/
- **Next.js 15 문서**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **TypeScript 핸드북**: https://www.typescriptlang.org/docs/
