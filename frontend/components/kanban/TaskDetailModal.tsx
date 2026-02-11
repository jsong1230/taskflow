'use client';

import { useEffect, useState, useCallback } from 'react';
import type { Task, TaskStatus, TaskPriority } from '@/types/api';
import { taskApi } from '@/lib/api';
import CommentSection from './CommentSection';

interface TaskDetailModalProps {
  projectId: number;
  taskId: number;
  onClose: () => void;
  onUpdate: () => void;
  onDelete: () => void;
}

export default function TaskDetailModal({
  projectId,
  taskId,
  onClose,
  onUpdate,
  onDelete,
}: TaskDetailModalProps) {
  const [task, setTask] = useState<Task | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchTask = useCallback(async () => {
    try {
      setIsLoading(true);
      const data = await taskApi.get(projectId, taskId);
      setTask(data);
    } catch (err) {
      console.error('Failed to fetch task:', err);
      alert('태스크를 불러오는데 실패했습니다.');
      onClose();
    } finally {
      setIsLoading(false);
    }
  }, [projectId, taskId, onClose]);

  useEffect(() => {
    fetchTask();
  }, [fetchTask]);

  const handleUpdateField = async (updates: Partial<Task>) => {
    if (!task) return;

    const previousTask = { ...task };
    setTask({ ...task, ...updates });

    try {
      await taskApi.update(projectId, taskId, updates);
      onUpdate();
    } catch (err) {
      console.error('Failed to update task:', err);
      setTask(previousTask);
      alert('태스크 수정에 실패했습니다.');
    }
  };

  const handleDelete = async () => {
    if (!confirm('정말로 이 태스크를 삭제하시겠습니까?')) return;

    setIsDeleting(true);
    try {
      await taskApi.delete(projectId, taskId);
      onDelete();
      onClose();
    } catch (err) {
      console.error('Failed to delete task:', err);
      alert('태스크 삭제에 실패했습니다.');
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
          <div className="text-center text-gray-600">로딩 중...</div>
        </div>
      </div>
    );
  }

  if (!task) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 헤더 */}
        <div className="flex items-start justify-between mb-4">
          <input
            type="text"
            value={task.title}
            onChange={(e) => handleUpdateField({ title: e.target.value })}
            onBlur={() => {
              if (!task.title.trim()) {
                setTask({ ...task, title: '제목 없음' });
                handleUpdateField({ title: '제목 없음' });
              }
            }}
            className="text-2xl font-bold flex-1 border-none outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1"
          />
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 ml-4"
          >
            ✕
          </button>
        </div>

        {/* 상태 & 우선순위 */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              상태
            </label>
            <select
              value={task.status}
              onChange={(e) =>
                handleUpdateField({ status: e.target.value as TaskStatus })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="todo">Todo</option>
              <option value="in_progress">In Progress</option>
              <option value="done">Done</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              우선순위
            </label>
            <select
              value={task.priority}
              onChange={(e) =>
                handleUpdateField({ priority: e.target.value as TaskPriority })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">낮음</option>
              <option value="medium">보통</option>
              <option value="high">높음</option>
              <option value="critical">긴급</option>
            </select>
          </div>
        </div>

        {/* 설명 */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            설명
          </label>
          <textarea
            value={task.description}
            onChange={(e) => handleUpdateField({ description: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            rows={4}
            placeholder="태스크 설명을 입력하세요..."
          />
        </div>

        {/* 메타 정보 */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg text-sm text-gray-600 space-y-1">
          <p>생성일: {new Date(task.created_at).toLocaleString('ko-KR')}</p>
          <p>수정일: {new Date(task.updated_at).toLocaleString('ko-KR')}</p>
          {task.assignee_id && <p>담당자 ID: {task.assignee_id}</p>}
        </div>

        {/* 댓글 섹션 */}
        <div className="mb-6">
          <CommentSection projectId={projectId} taskId={taskId} />
        </div>

        {/* 하단 버튼 */}
        <div className="flex justify-between pt-4 border-t">
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {isDeleting ? '삭제 중...' : '삭제'}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}
