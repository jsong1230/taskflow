'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { projectApi, taskApi, authApi } from '@/lib/api';
import type { Project, Task, User } from '@/types/api';
import ProjectStatsCard from '@/components/dashboard/ProjectStatsCard';
import AssignedTasksList from '@/components/dashboard/AssignedTasksList';

interface ProjectWithTasks {
  project: Project;
  tasks: Task[];
}

export default function DashboardPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [projectsWithTasks, setProjectsWithTasks] = useState<ProjectWithTasks[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // 현재 사용자 정보 가져오기
      const user = await authApi.me();
      setCurrentUser(user);

      // 프로젝트 목록 가져오기
      const projects = await projectApi.list();

      // 각 프로젝트의 태스크 가져오기
      const projectsData = await Promise.all(
        projects.map(async (project) => {
          const tasks = await taskApi.list(project.id);
          return { project, tasks };
        })
      );

      setProjectsWithTasks(projectsData);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('대시보드 데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 내게 배정된 태스크 필터링
  const assignedTasks = projectsWithTasks.flatMap(({ project, tasks }) =>
    tasks
      .filter((task) => task.assignee_id === currentUser?.id)
      .map((task) => ({
        ...task,
        projectId: project.id,
        projectName: project.name,
      }))
  );

  // 전체 통계
  const totalTasks = projectsWithTasks.reduce(
    (sum, { tasks }) => sum + tasks.length,
    0
  );
  const completedTasks = projectsWithTasks.reduce(
    (sum, { tasks }) => sum + tasks.filter((t) => t.status === 'done').length,
    0
  );
  const inProgressTasks = projectsWithTasks.reduce(
    (sum, { tasks }) => sum + tasks.filter((t) => t.status === 'in_progress').length,
    0
  );

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-gray-600">로딩 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
              {currentUser && (
                <p className="text-gray-600 mt-1">
                  안녕하세요, {currentUser.name}님! 👋
                </p>
              )}
            </div>
            <Link
              href="/projects"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              프로젝트 목록
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 전체 통계 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">프로젝트</div>
            <div className="text-3xl font-bold text-gray-900">
              {projectsWithTasks.length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">전체 태스크</div>
            <div className="text-3xl font-bold text-gray-900">{totalTasks}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">진행 중</div>
            <div className="text-3xl font-bold text-blue-600">{inProgressTasks}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">완료</div>
            <div className="text-3xl font-bold text-green-600">{completedTasks}</div>
          </div>
        </div>

        {/* 내게 배정된 태스크 */}
        {assignedTasks.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              내게 배정된 태스크 ({assignedTasks.length})
            </h2>
            <AssignedTasksList tasks={assignedTasks} />
          </div>
        )}

        {/* 프로젝트별 현황 */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            프로젝트 현황
          </h2>
          {projectsWithTasks.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200">
              <p className="text-gray-500 mb-4">아직 프로젝트가 없습니다.</p>
              <Link
                href="/projects"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                첫 프로젝트를 만들어보세요
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projectsWithTasks.map(({ project, tasks }) => (
                <ProjectStatsCard
                  key={project.id}
                  project={project}
                  tasks={tasks}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
