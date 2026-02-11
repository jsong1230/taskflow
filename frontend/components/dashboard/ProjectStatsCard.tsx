import Link from 'next/link';
import type { Project, Task } from '@/types/api';
import ProgressBar from './ProgressBar';

interface ProjectStatsCardProps {
  project: Project;
  tasks: Task[];
}

export default function ProjectStatsCard({ project, tasks }: ProjectStatsCardProps) {
  const todoCount = tasks.filter((t) => t.status === 'todo').length;
  const inProgressCount = tasks.filter((t) => t.status === 'in_progress').length;
  const doneCount = tasks.filter((t) => t.status === 'done').length;
  const totalCount = tasks.length;

  return (
    <Link
      href={`/projects/${project.id}`}
      className="block bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200"
    >
      {/* 프로젝트 이름 */}
      <h3 className="text-xl font-bold text-gray-900 mb-2">{project.name}</h3>
      {project.description && (
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {project.description}
        </p>
      )}

      {/* 진행률 */}
      <div className="mb-4">
        <ProgressBar total={totalCount} completed={doneCount} showLabel={false} />
        <p className="text-xs text-gray-600 mt-1">
          {doneCount}/{totalCount} 완료 (
          {totalCount === 0 ? 0 : Math.round((doneCount / totalCount) * 100)}%)
        </p>
      </div>

      {/* 상태별 태스크 수 */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-700">{todoCount}</div>
          <div className="text-xs text-gray-500 mt-1">Todo</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{inProgressCount}</div>
          <div className="text-xs text-gray-500 mt-1">In Progress</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{doneCount}</div>
          <div className="text-xs text-gray-500 mt-1">Done</div>
        </div>
      </div>

      {/* 바로가기 힌트 */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <span className="text-sm text-blue-600 hover:text-blue-700 font-medium">
          칸반 보드 열기 →
        </span>
      </div>
    </Link>
  );
}
