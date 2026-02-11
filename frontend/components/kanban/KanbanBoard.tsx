'use client';

import { useState, useEffect, useCallback } from 'react';
import type { Task, TaskStatus } from '@/types/api';
import { taskApi } from '@/lib/api';
import KanbanColumn from './KanbanColumn';

interface KanbanBoardProps {
  projectId: number;
  onTaskClick: (taskId: number) => void;
  onCreateTask: (status: TaskStatus) => void;
}

const COLUMNS: { status: TaskStatus; title: string }[] = [
  { status: 'todo', title: 'Todo' },
  { status: 'in_progress', title: 'In Progress' },
  { status: 'done', title: 'Done' },
];

export default function KanbanBoard({
  projectId,
  onTaskClick,
  onCreateTask,
}: KanbanBoardProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [draggedTaskId, setDraggedTaskId] = useState<number | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await taskApi.list(projectId);
      setTasks(data);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      alert('태스크 목록을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleDragStart = (e: React.DragEvent, taskId: number) => {
    setDraggedTaskId(taskId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e: React.DragEvent, newStatus: TaskStatus) => {
    e.preventDefault();

    if (!draggedTaskId) return;

    const task = tasks.find((t) => t.id === draggedTaskId);
    if (!task || task.status === newStatus) {
      setDraggedTaskId(null);
      return;
    }

    // 낙관적 업데이트 (즉시 UI 업데이트)
    const previousTasks = [...tasks];
    setTasks((prev) =>
      prev.map((t) =>
        t.id === draggedTaskId ? { ...t, status: newStatus } : t
      )
    );

    try {
      // 서버에 상태 변경 요청
      await taskApi.updateStatus(projectId, draggedTaskId, { status: newStatus });
    } catch (err) {
      // 실패 시 롤백
      console.error('Failed to update task status:', err);
      setTasks(previousTasks);
      alert('태스크 상태 변경에 실패했습니다.');
    } finally {
      setDraggedTaskId(null);
    }
  };

  const getTasksByStatus = (status: TaskStatus) => {
    return tasks.filter((task) => task.status === status);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {COLUMNS.map((column) => (
        <KanbanColumn
          key={column.status}
          status={column.status}
          title={column.title}
          tasks={getTasksByStatus(column.status)}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onDragStart={handleDragStart}
          onTaskClick={onTaskClick}
          onCreateTask={onCreateTask}
        />
      ))}
    </div>
  );
}
