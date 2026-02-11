'use client';

import type { Task, TaskStatus } from '@/types/api';
import TaskCard from './TaskCard';

interface KanbanColumnProps {
  status: TaskStatus;
  title: string;
  tasks: Task[];
  onDragOver: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent, newStatus: TaskStatus) => void;
  onDragStart: (e: React.DragEvent, taskId: number) => void;
  onTaskClick: (taskId: number) => void;
  onCreateTask: (status: TaskStatus) => void;
}

export default function KanbanColumn({
  status,
  title,
  tasks,
  onDragOver,
  onDrop,
  onDragStart,
  onTaskClick,
  onCreateTask,
}: KanbanColumnProps) {
  return (
    <div className="flex flex-col bg-gray-100 rounded-lg p-4 min-h-[600px]">
      {/* 컬럼 헤더 */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-700">
          {title}
          <span className="ml-2 text-sm font-normal text-gray-500">
            ({tasks.length})
          </span>
        </h2>
      </div>

      {/* 드롭 영역 */}
      <div
        onDragOver={onDragOver}
        onDrop={(e) => onDrop(e, status)}
        className="flex-1 space-y-3 min-h-[200px]"
      >
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onDragStart={onDragStart}
            onClick={onTaskClick}
          />
        ))}
      </div>

      {/* 새 태스크 추가 버튼 */}
      <button
        onClick={() => onCreateTask(status)}
        className="mt-4 w-full border-2 border-dashed border-gray-300 rounded-lg p-3 text-gray-500 hover:border-gray-400 hover:text-gray-600 transition-colors text-sm font-medium"
      >
        + 태스크 추가
      </button>
    </div>
  );
}
