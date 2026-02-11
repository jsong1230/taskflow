'use client';

import type { Task, TaskPriority } from '@/types/api';

interface TaskCardProps {
  task: Task;
  onDragStart: (e: React.DragEvent, taskId: number) => void;
  onClick: (taskId: number) => void;
}

const PRIORITY_CONFIG: Record<
  TaskPriority,
  { label: string; color: string; bgColor: string }
> = {
  low: { label: '낮음', color: 'text-gray-700', bgColor: 'bg-gray-100' },
  medium: { label: '보통', color: 'text-blue-700', bgColor: 'bg-blue-100' },
  high: { label: '높음', color: 'text-orange-700', bgColor: 'bg-orange-100' },
  critical: { label: '긴급', color: 'text-red-700', bgColor: 'bg-red-100' },
};

export default function TaskCard({ task, onDragStart, onClick }: TaskCardProps) {
  const priorityConfig = PRIORITY_CONFIG[task.priority];

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, task.id)}
      onClick={() => onClick(task.id)}
      className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-move border border-gray-200"
    >
      {/* 제목 */}
      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
        {task.title}
      </h3>

      {/* 설명 (있는 경우) */}
      {task.description && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* 하단 영역: 우선순위 뱃지 & 담당자 */}
      <div className="flex items-center justify-between mt-3">
        {/* 우선순위 뱃지 */}
        <span
          className={`text-xs font-medium px-2 py-1 rounded ${priorityConfig.bgColor} ${priorityConfig.color}`}
        >
          {priorityConfig.label}
        </span>

        {/* 담당자 아바타 */}
        {task.assignee_id && (
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-semibold">
              {task.assignee_id.toString().slice(-2)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
