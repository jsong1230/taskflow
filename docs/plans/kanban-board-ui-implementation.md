# 칸반 보드 UI 구현 계획

## 1. 개요

프로젝트의 태스크를 시각적으로 관리할 수 있는 칸반 보드 UI를 구현합니다. Todo, In Progress, Done 세 가지 상태 컬럼을 제공하며, 드래그 앤 드롭으로 태스크 상태를 변경할 수 있습니다.

### 주요 기능
- ✅ 세 가지 상태 컬럼 (Todo, In Progress, Done)
- ✅ 드래그 앤 드롭으로 태스크 이동
- ✅ 태스크 카드 클릭 시 상세 모달 표시
- ✅ 새 태스크 생성 기능
- ✅ 실시간 API 연동

---

## 2. 컴포넌트 구조

```
frontend/
├── app/
│   └── projects/
│       └── [id]/
│           └── board/
│               └── page.tsx          # 칸반 보드 페이지 (Server Component)
├── components/
│   └── kanban/
│       ├── KanbanBoard.tsx           # 칸반 보드 메인 컨테이너 (Client Component)
│       ├── KanbanColumn.tsx          # 컬럼 컴포넌트
│       ├── TaskCard.tsx              # 태스크 카드 컴포넌트
│       ├── TaskDetailModal.tsx       # 태스크 상세 모달
│       ├── CreateTaskModal.tsx       # 태스크 생성 모달
│       └── DragOverlay.tsx           # 드래그 중 오버레이
├── lib/
│   └── api/
│       └── tasks.ts                  # 태스크 API 클라이언트
├── types/
│   └── kanban.ts                     # 칸반 관련 타입 정의
└── hooks/
    ├── useKanbanBoard.ts             # 칸반 보드 상태 관리 훅
    └── useTasks.ts                   # 태스크 데이터 페칭 훅
```

### 2.1 KanbanBoard (Client Component)

**역할**: 칸반 보드의 최상위 컴포넌트, 드래그 앤 드롭 컨텍스트 제공

```typescript
'use client';

interface KanbanBoardProps {
  projectId: number;
  initialTasks: Task[];
}

export default function KanbanBoard({ projectId, initialTasks }: KanbanBoardProps) {
  // 드래그 앤 드롭 상태 관리
  // 태스크 목록 상태 관리
  // 모달 상태 관리

  return (
    <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-3 gap-4">
        <KanbanColumn status="TODO" tasks={todoTasks} />
        <KanbanColumn status="IN_PROGRESS" tasks={inProgressTasks} />
        <KanbanColumn status="DONE" tasks={doneTasks} />
      </div>

      <TaskDetailModal />
      <CreateTaskModal />
    </DndContext>
  );
}
```

**주요 기능**:
- 드래그 앤 드롭 컨텍스트 제공
- 태스크 목록을 상태별로 필터링
- 모달 열기/닫기 제어
- API 호출을 통한 태스크 상태 업데이트

---

### 2.2 KanbanColumn

**역할**: 각 상태별 컬럼 렌더링 및 드롭 영역 제공

```typescript
interface KanbanColumnProps {
  status: TaskStatus;
  tasks: Task[];
}

export function KanbanColumn({ status, tasks }: KanbanColumnProps) {
  const { isOver, setNodeRef } = useDroppable({ id: status });

  return (
    <div ref={setNodeRef} className={cn("bg-gray-100 rounded-lg p-4", isOver && "bg-gray-200")}>
      <h2 className="font-bold text-lg mb-4">{COLUMN_TITLES[status]}</h2>
      <div className="space-y-3">
        {tasks.map(task => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
      <button className="mt-4 w-full border-2 border-dashed border-gray-300 rounded p-2">
        + 태스크 추가
      </button>
    </div>
  );
}
```

**주요 기능**:
- 드롭 가능한 영역 설정
- 태스크 카드 목록 렌더링
- 컬럼별 헤더 표시
- 새 태스크 추가 버튼

---

### 2.3 TaskCard

**역할**: 개별 태스크 카드 표시 및 드래그 가능하게 설정

```typescript
interface TaskCardProps {
  task: Task;
}

export function TaskCard({ task }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: task.id,
    data: { task }
  });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
  } : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={cn(
        "bg-white rounded-lg p-4 shadow cursor-move",
        isDragging && "opacity-50"
      )}
      onClick={() => openTaskDetailModal(task.id)}
    >
      <h3 className="font-semibold mb-2">{task.title}</h3>
      {task.description && (
        <p className="text-sm text-gray-600 line-clamp-2">{task.description}</p>
      )}
      <div className="flex items-center justify-between mt-3">
        {task.assignee && (
          <div className="flex items-center gap-2">
            <Avatar size="sm" name={task.assignee.name} />
            <span className="text-xs">{task.assignee.name}</span>
          </div>
        )}
        <span className="text-xs text-gray-500">{formatDate(task.dueDate)}</span>
      </div>
    </div>
  );
}
```

**주요 기능**:
- 드래그 가능한 카드
- 태스크 기본 정보 표시 (제목, 설명, 담당자, 마감일)
- 클릭 시 상세 모달 열기
- 드래그 중 시각적 피드백

---

### 2.4 TaskDetailModal

**역할**: 태스크 상세 정보 표시 및 수정

```typescript
interface TaskDetailModalProps {
  taskId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export function TaskDetailModal({ taskId, isOpen, onClose }: TaskDetailModalProps) {
  const { data: task, isLoading } = useTask(taskId);

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalHeader>
        <input
          type="text"
          value={task?.title}
          onChange={(e) => updateTask({ title: e.target.value })}
          className="text-xl font-bold border-none"
        />
      </ModalHeader>

      <ModalBody>
        <div className="space-y-4">
          <div>
            <label>상태</label>
            <select value={task?.status} onChange={handleStatusChange}>
              <option value="TODO">Todo</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="DONE">Done</option>
            </select>
          </div>

          <div>
            <label>설명</label>
            <textarea
              value={task?.description}
              onChange={(e) => updateTask({ description: e.target.value })}
            />
          </div>

          <div>
            <label>담당자</label>
            <UserSelect
              value={task?.assignee_id}
              onChange={(userId) => updateTask({ assignee_id: userId })}
            />
          </div>

          <div>
            <label>마감일</label>
            <DatePicker
              value={task?.due_date}
              onChange={(date) => updateTask({ due_date: date })}
            />
          </div>

          <CommentSection taskId={taskId} />
        </div>
      </ModalBody>

      <ModalFooter>
        <button onClick={handleDelete}>삭제</button>
        <button onClick={onClose}>닫기</button>
      </ModalFooter>
    </Modal>
  );
}
```

**주요 기능**:
- 태스크 전체 정보 표시
- 인라인 편집 (제목, 설명, 상태, 담당자, 마감일)
- 댓글 목록 및 작성
- 태스크 삭제

---

### 2.5 CreateTaskModal

**역할**: 새 태스크 생성 폼

```typescript
interface CreateTaskModalProps {
  projectId: number;
  defaultStatus?: TaskStatus;
  isOpen: boolean;
  onClose: () => void;
}

export function CreateTaskModal({ projectId, defaultStatus, isOpen, onClose }: CreateTaskModalProps) {
  const [formData, setFormData] = useState<CreateTaskForm>({
    title: '',
    description: '',
    status: defaultStatus || 'TODO',
    assignee_id: null,
    due_date: null,
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await createTask(projectId, formData);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        <ModalHeader>새 태스크 만들기</ModalHeader>

        <ModalBody>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="태스크 제목"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />

            <textarea
              placeholder="상세 설명 (선택사항)"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />

            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as TaskStatus })}
            >
              <option value="TODO">Todo</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="DONE">Done</option>
            </select>
          </div>
        </ModalBody>

        <ModalFooter>
          <button type="button" onClick={onClose}>취소</button>
          <button type="submit">만들기</button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
```

**주요 기능**:
- 태스크 기본 정보 입력 폼
- 기본 상태 설정 (컬럼의 + 버튼 클릭 시)
- 폼 유효성 검사
- API 호출로 태스크 생성

---

## 3. 드래그 앤 드롭 구현

### 3.1 라이브러리 선택: @dnd-kit

**선택 이유**:
- ✅ React 18+ 및 Next.js 15와 완벽 호환
- ✅ TypeScript 완벽 지원
- ✅ 접근성 (키보드 네비게이션) 내장
- ✅ 모바일 터치 지원
- ✅ 가볍고 모듈화된 구조
- ✅ react-beautiful-dnd 대비 유지보수 활발

**설치**:
```bash
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

### 3.2 드래그 앤 드롭 플로우

```typescript
// KanbanBoard.tsx
import { DndContext, DragEndEvent, DragOverlay, DragStartEvent } from '@dnd-kit/core';

function KanbanBoard({ projectId, initialTasks }: KanbanBoardProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [activeId, setActiveId] = useState<number | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor)
  );

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as number);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) return;

    const taskId = active.id as number;
    const newStatus = over.id as TaskStatus;

    // 낙관적 업데이트 (Optimistic Update)
    setTasks(prev =>
      prev.map(task =>
        task.id === taskId ? { ...task, status: newStatus } : task
      )
    );

    // API 호출
    try {
      await updateTaskStatus(taskId, newStatus);
    } catch (error) {
      // 실패 시 롤백
      setTasks(initialTasks);
      toast.error('태스크 상태 변경에 실패했습니다.');
    }

    setActiveId(null);
  };

  return (
    <DndContext
      sensors={sensors}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      {/* 컬럼들 */}

      <DragOverlay>
        {activeId ? <TaskCard task={tasks.find(t => t.id === activeId)!} /> : null}
      </DragOverlay>
    </DndContext>
  );
}
```

### 3.3 드롭 가능 영역 설정

```typescript
// KanbanColumn.tsx
import { useDroppable } from '@dnd-kit/core';

function KanbanColumn({ status, tasks }: KanbanColumnProps) {
  const { isOver, setNodeRef } = useDroppable({
    id: status,
  });

  return (
    <div
      ref={setNodeRef}
      className={cn(
        "min-h-[500px] bg-gray-50 rounded-lg p-4 transition-colors",
        isOver && "bg-blue-50 ring-2 ring-blue-300"
      )}
    >
      {/* 태스크 카드들 */}
    </div>
  );
}
```

### 3.4 드래그 가능 항목 설정

```typescript
// TaskCard.tsx
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';

function TaskCard({ task }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: task.id,
    data: { task },
  });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className="cursor-grab active:cursor-grabbing"
    >
      {/* 카드 내용 */}
    </div>
  );
}
```

---

## 4. 상태 관리 전략

### 4.1 로컬 상태 (useState)

**용도**: UI 상태 관리
- 모달 열기/닫기 상태
- 드래그 중인 태스크 ID
- 폼 입력 데이터

```typescript
const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
```

### 4.2 서버 상태 (React Query / SWR)

**용도**: 서버 데이터 캐싱 및 동기화

**추천**: **SWR** (Next.js와 Vercel에서 개발, Next.js와 궁합 좋음)

```bash
npm install swr
```

```typescript
// hooks/useTasks.ts
import useSWR from 'swr';

export function useTasks(projectId: number) {
  const { data, error, mutate } = useSWR<Task[]>(
    `/api/projects/${projectId}/tasks`,
    fetcher,
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
    }
  );

  return {
    tasks: data ?? [],
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}

export function useTask(taskId: number | null) {
  const { data, error, mutate } = useSWR<Task>(
    taskId ? `/api/tasks/${taskId}` : null,
    fetcher
  );

  return {
    task: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}
```

**SWR의 장점**:
- 자동 캐싱 및 재검증
- 낙관적 업데이트 지원
- 포커스 시 자동 갱신
- 실시간 협업 시 유리

### 4.3 전역 상태 (Context API - 선택사항)

**용도**: 여러 컴포넌트에서 공유하는 상태 (필요시에만)

```typescript
// contexts/KanbanContext.tsx
'use client';

interface KanbanContextValue {
  selectedTaskId: number | null;
  setSelectedTaskId: (id: number | null) => void;
  openCreateModal: (status?: TaskStatus) => void;
  closeCreateModal: () => void;
}

const KanbanContext = createContext<KanbanContextValue | undefined>(undefined);

export function KanbanProvider({ children }: { children: ReactNode }) {
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [createModalStatus, setCreateModalStatus] = useState<TaskStatus | null>(null);

  const value = {
    selectedTaskId,
    setSelectedTaskId,
    openCreateModal: (status?: TaskStatus) => setCreateModalStatus(status || 'TODO'),
    closeCreateModal: () => setCreateModalStatus(null),
  };

  return <KanbanContext.Provider value={value}>{children}</KanbanContext.Provider>;
}

export function useKanban() {
  const context = useContext(KanbanContext);
  if (!context) throw new Error('useKanban must be used within KanbanProvider');
  return context;
}
```

### 4.4 낙관적 업데이트 패턴

드래그 앤 드롭 시 즉각적인 UI 반응을 위해 낙관적 업데이트 사용:

```typescript
const handleDragEnd = async (event: DragEndEvent) => {
  const { active, over } = event;
  if (!over) return;

  const taskId = active.id as number;
  const newStatus = over.id as TaskStatus;

  // 1. 즉시 UI 업데이트 (낙관적)
  mutate(
    `/api/projects/${projectId}/tasks`,
    (tasks: Task[]) =>
      tasks.map(task =>
        task.id === taskId ? { ...task, status: newStatus } : task
      ),
    { revalidate: false }
  );

  // 2. 서버에 요청
  try {
    await updateTaskStatus(taskId, newStatus);
    // 3. 성공 시 서버 데이터로 재검증
    mutate(`/api/projects/${projectId}/tasks`);
  } catch (error) {
    // 4. 실패 시 원래 상태로 되돌림
    mutate(`/api/projects/${projectId}/tasks`);
    toast.error('태스크 이동에 실패했습니다.');
  }
};
```

---

## 5. API 통신

### 5.1 API 클라이언트 함수

```typescript
// lib/api/tasks.ts

export async function fetchTasks(projectId: number): Promise<Task[]> {
  const response = await fetch(`/api/projects/${projectId}/tasks`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) throw new Error('Failed to fetch tasks');
  return response.json();
}

export async function fetchTask(taskId: number): Promise<Task> {
  const response = await fetch(`/api/tasks/${taskId}`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) throw new Error('Failed to fetch task');
  return response.json();
}

export async function updateTaskStatus(
  taskId: number,
  status: TaskStatus
): Promise<Task> {
  const response = await fetch(`/api/tasks/${taskId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ status }),
  });

  if (!response.ok) throw new Error('Failed to update task status');
  return response.json();
}

export async function createTask(
  projectId: number,
  data: CreateTaskInput
): Promise<Task> {
  const response = await fetch(`/api/projects/${projectId}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) throw new Error('Failed to create task');
  return response.json();
}

export async function updateTask(
  taskId: number,
  data: Partial<UpdateTaskInput>
): Promise<Task> {
  const response = await fetch(`/api/tasks/${taskId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) throw new Error('Failed to update task');
  return response.json();
}

export async function deleteTask(taskId: number): Promise<void> {
  const response = await fetch(`/api/tasks/${taskId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) throw new Error('Failed to delete task');
}
```

### 5.2 SWR fetcher 설정

```typescript
// lib/api/fetcher.ts

export const fetcher = async (url: string) => {
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${getToken()}`,
    },
  });

  if (!response.ok) {
    const error = new Error('An error occurred while fetching the data.');
    error.info = await response.json();
    error.status = response.status;
    throw error;
  }

  return response.json();
};
```

---

## 6. 타입 정의

```typescript
// types/kanban.ts

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'DONE';

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  project_id: number;
  assignee_id?: number;
  assignee?: User;
  due_date?: string;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  username: string;
  name: string;
  email: string;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  status: TaskStatus;
  assignee_id?: number;
  due_date?: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  status?: TaskStatus;
  assignee_id?: number;
  due_date?: string;
}

export interface Column {
  id: TaskStatus;
  title: string;
  tasks: Task[];
}

export const COLUMN_TITLES: Record<TaskStatus, string> = {
  TODO: 'Todo',
  IN_PROGRESS: 'In Progress',
  DONE: 'Done',
};

export const COLUMN_ORDER: TaskStatus[] = ['TODO', 'IN_PROGRESS', 'DONE'];
```

---

## 7. 스타일링 가이드

### 7.1 Tailwind CSS 클래스 예시

```typescript
// 칸반 보드 컨테이너
<div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6">

// 컬럼
<div className="bg-gray-50 rounded-lg p-4 min-h-[600px]">

// 컬럼 헤더
<h2 className="text-lg font-bold mb-4 text-gray-700">

// 태스크 카드
<div className="bg-white rounded-lg shadow-sm p-4 cursor-grab hover:shadow-md transition-shadow">

// 드래그 중인 카드
<div className="opacity-50 cursor-grabbing">

// 드롭 가능 영역 (hover)
<div className="bg-blue-50 ring-2 ring-blue-300">
```

### 7.2 반응형 디자인

- 모바일: 단일 컬럼 (탭으로 전환)
- 태블릿: 2컬럼
- 데스크톱: 3컬럼

```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

---

## 8. 구현 순서

### Phase 1: 기본 레이아웃 및 정적 UI ✅

1. ✅ 타입 정의 작성 (`types/kanban.ts`)
2. ✅ 컬럼 컴포넌트 구현 (정적 데이터)
3. ✅ 태스크 카드 컴포넌트 구현 (정적 데이터)
4. ✅ 칸반 보드 레이아웃 구성
5. ✅ Tailwind CSS 스타일링

**예상 소요 시간**: 2-3시간

### Phase 2: API 연동 및 데이터 페칭 🔄

1. ✅ API 클라이언트 함수 작성
2. ✅ SWR 설정 및 커스텀 훅 구현
3. ✅ 서버에서 초기 데이터 페칭 (Server Component)
4. ✅ 클라이언트에서 실시간 데이터 동기화

**예상 소요 시간**: 2-3시간

### Phase 3: 드래그 앤 드롭 구현 🎯

1. ✅ @dnd-kit 라이브러리 설치 및 설정
2. ✅ DndContext 설정
3. ✅ 드래그 가능한 카드 구현
4. ✅ 드롭 가능한 컬럼 구현
5. ✅ 드래그 이벤트 핸들러 구현
6. ✅ 낙관적 업데이트 로직 추가
7. ✅ 에러 처리 및 롤백

**예상 소요 시간**: 3-4시간

### Phase 4: 모달 구현 📝

1. ✅ 태스크 상세 모달 UI 구현
2. ✅ 인라인 편집 기능 구현
3. ✅ 새 태스크 생성 모달 구현
4. ✅ 폼 유효성 검사
5. ✅ API 연동

**예상 소요 시간**: 3-4시간

### Phase 5: 추가 기능 및 개선 🚀

1. ✅ 담당자 선택 UI
2. ✅ 마감일 선택 (날짜 피커)
3. ✅ 댓글 기능
4. ✅ 태스크 검색/필터링
5. ✅ 키보드 단축키 (접근성)
6. ✅ 로딩 상태 UI
7. ✅ 에러 바운더리

**예상 소요 시간**: 4-5시간

### Phase 6: 테스트 및 최적화 🧪

1. ✅ 컴포넌트 단위 테스트
2. ✅ E2E 테스트 (Playwright)
3. ✅ 성능 최적화 (메모이제이션, 가상화)
4. ✅ 접근성 검증
5. ✅ 모바일 반응형 테스트

**예상 소요 시간**: 3-4시간

---

## 9. 성능 최적화

### 9.1 컴포넌트 메모이제이션

```typescript
export const TaskCard = memo(function TaskCard({ task }: TaskCardProps) {
  // ...
}, (prevProps, nextProps) => {
  return prevProps.task.id === nextProps.task.id &&
         prevProps.task.status === nextProps.task.status &&
         prevProps.task.title === nextProps.task.title;
});
```

### 9.2 가상 스크롤링 (태스크가 많을 경우)

```bash
npm install react-virtual
```

```typescript
import { useVirtual } from 'react-virtual';

function KanbanColumn({ tasks }: KanbanColumnProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtual({
    size: tasks.length,
    parentRef,
    estimateSize: useCallback(() => 120, []),
  });

  return (
    <div ref={parentRef} className="overflow-auto h-full">
      <div style={{ height: `${rowVirtualizer.totalSize}px` }}>
        {rowVirtualizer.virtualItems.map(virtualRow => (
          <TaskCard key={tasks[virtualRow.index].id} task={tasks[virtualRow.index]} />
        ))}
      </div>
    </div>
  );
}
```

### 9.3 디바운싱 (검색/필터)

```typescript
import { useDebouncedValue } from '@/hooks/useDebounce';

const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebouncedValue(searchTerm, 300);
```

---

## 10. 접근성 (A11y)

### 10.1 키보드 네비게이션

- @dnd-kit은 키보드 네비게이션을 자동으로 지원
- Space/Enter로 드래그 시작
- 화살표 키로 이동
- Escape로 취소

### 10.2 스크린 리더 지원

```typescript
<div
  role="button"
  tabIndex={0}
  aria-label={`${task.title} 태스크 카드`}
  aria-describedby={`task-desc-${task.id}`}
>
  <h3 id={`task-title-${task.id}`}>{task.title}</h3>
  <p id={`task-desc-${task.id}`}>{task.description}</p>
</div>
```

### 10.3 포커스 관리

```typescript
const modalRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (isOpen) {
    modalRef.current?.focus();
  }
}, [isOpen]);
```

---

## 11. 에러 처리

### 11.1 에러 바운더리

```typescript
// components/ErrorBoundary.tsx
'use client';

export class KanbanErrorBoundary extends Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 text-center">
          <h2>칸반 보드를 불러오는 중 오류가 발생했습니다.</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            다시 시도
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### 11.2 API 에러 처리

```typescript
const { tasks, error, isLoading } = useTasks(projectId);

if (error) {
  return (
    <div className="p-8 text-center">
      <p className="text-red-600">태스크를 불러오는 데 실패했습니다.</p>
      <button onClick={() => mutate()}>다시 시도</button>
    </div>
  );
}
```

### 11.3 Toast 알림

```bash
npm install sonner
```

```typescript
import { toast } from 'sonner';

const handleDragEnd = async (event: DragEndEvent) => {
  try {
    await updateTaskStatus(taskId, newStatus);
    toast.success('태스크가 이동되었습니다.');
  } catch (error) {
    toast.error('태스크 이동에 실패했습니다.');
  }
};
```

---

## 12. 배포 전 체크리스트

- [ ] 모든 컴포넌트에 TypeScript 타입 정의 완료
- [ ] API 에러 처리 구현
- [ ] 로딩 상태 UI 추가
- [ ] 빈 상태 UI (태스크 없을 때)
- [ ] 모바일 반응형 확인
- [ ] 접근성 (키보드, 스크린 리더) 테스트
- [ ] 드래그 앤 드롭 성능 테스트 (50+ 태스크)
- [ ] 브라우저 호환성 확인 (Chrome, Firefox, Safari)
- [ ] 라이트모드/다크모드 지원 (선택사항)

---

## 13. 향후 개선 사항

- **실시간 협업**: WebSocket으로 다른 사용자의 변경사항 실시간 반영
- **커스텀 컬럼**: 사용자 정의 상태 컬럼 추가
- **스윔레인**: 담당자별, 우선순위별 그룹핑
- **태스크 템플릿**: 반복 태스크 생성 자동화
- **일괄 작업**: 여러 태스크 한 번에 이동/삭제
- **활동 로그**: 태스크 히스토리 추적
- **알림**: 담당자 변경, 마감일 임박 시 알림

---

## 참고 자료

- [@dnd-kit 공식 문서](https://docs.dndkit.com/)
- [SWR 공식 문서](https://swr.vercel.app/)
- [Next.js 15 App Router 가이드](https://nextjs.org/docs)
- [Tailwind CSS 컴포넌트 예제](https://tailwindui.com/)
- [React 접근성 가이드](https://react.dev/learn/accessibility)
