'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { projectApi } from '@/lib/api';
import type { ProjectDetail, TaskStatus } from '@/types/api';
import KanbanBoard from '@/components/kanban/KanbanBoard';
import CreateTaskForm from '@/components/kanban/CreateTaskForm';
import TaskDetailModal from '@/components/kanban/TaskDetailModal';

export default function ProjectPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = Number(params.id);

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [createTaskStatus, setCreateTaskStatus] = useState<TaskStatus | null>(null);
  const [boardRefreshKey, setBoardRefreshKey] = useState(0);

  const fetchProject = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await projectApi.get(projectId);
      setProject(data);
    } catch (err) {
      console.error('Failed to fetch project:', err);
      alert('프로젝트를 불러오는데 실패했습니다.');
      router.push('/projects');
    } finally {
      setIsLoading(false);
    }
  }, [projectId, router]);

  useEffect(() => {
    if (!projectId) return;
    fetchProject();
  }, [projectId, fetchProject]);

  const handleTaskClick = (taskId: number) => {
    setSelectedTaskId(taskId);
  };

  const handleCreateTask = (status: TaskStatus) => {
    setCreateTaskStatus(status);
  };

  const handleTaskCreated = () => {
    setBoardRefreshKey((prev) => prev + 1);
  };

  const handleTaskUpdated = () => {
    setBoardRefreshKey((prev) => prev + 1);
  };

  const handleTaskDeleted = () => {
    setBoardRefreshKey((prev) => prev + 1);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">로딩 중...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">프로젝트를 찾을 수 없습니다.</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4 mb-2">
            <Link
              href="/projects"
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              ← 프로젝트 목록
            </Link>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
          {project.description && (
            <p className="text-gray-600 mt-2">{project.description}</p>
          )}
        </div>
      </div>

      {/* 칸반 보드 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <KanbanBoard
          key={boardRefreshKey}
          projectId={projectId}
          onTaskClick={handleTaskClick}
          onCreateTask={handleCreateTask}
        />
      </div>

      {/* TaskDetailModal */}
      {selectedTaskId && (
        <TaskDetailModal
          projectId={projectId}
          taskId={selectedTaskId}
          onClose={() => setSelectedTaskId(null)}
          onUpdate={handleTaskUpdated}
          onDelete={handleTaskDeleted}
        />
      )}

      {/* CreateTaskForm 모달 */}
      {createTaskStatus && (
        <CreateTaskForm
          projectId={projectId}
          initialStatus={createTaskStatus}
          onClose={() => setCreateTaskStatus(null)}
          onSuccess={handleTaskCreated}
        />
      )}
    </div>
  );
}
