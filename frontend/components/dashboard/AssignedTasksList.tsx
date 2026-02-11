import Link from 'next/link';
import type { Task, TaskPriority, TaskStatus } from '@/types/api';

interface AssignedTasksListProps {
  tasks: Array<Task & { projectId: number; projectName: string }>;
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

const STATUS_CONFIG: Record<TaskStatus, { label: string; color: string }> = {
  todo: { label: 'Todo', color: 'text-gray-600' },
  in_progress: { label: 'In Progress', color: 'text-blue-600' },
  done: { label: 'Done', color: 'text-green-600' },
};

export default function AssignedTasksList({ tasks }: AssignedTasksListProps) {
  if (tasks.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200">
        <p className="text-gray-500">현재 배정된 태스크가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="divide-y divide-gray-100">
        {tasks.map((task) => {
          const priorityConfig = PRIORITY_CONFIG[task.priority];
          const statusConfig = STATUS_CONFIG[task.status];

          return (
            <Link
              key={task.id}
              href={`/projects/${task.projectId}`}
              className="block p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* 제목 */}
                  <h4 className="font-semibold text-gray-900 mb-1">
                    {task.title}
                  </h4>

                  {/* 설명 */}
                  {task.description && (
                    <p className="text-sm text-gray-600 mb-2 line-clamp-1">
                      {task.description}
                    </p>
                  )}

                  {/* 프로젝트 & 상태 & 우선순위 */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-gray-500">
                      📁 {task.projectName}
                    </span>
                    <span className={`text-xs font-medium ${statusConfig.color}`}>
                      • {statusConfig.label}
                    </span>
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded ${priorityConfig.bgColor} ${priorityConfig.color}`}
                    >
                      {priorityConfig.label}
                    </span>
                  </div>
                </div>

                {/* 화살표 */}
                <div className="ml-4 text-gray-400">
                  →
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
