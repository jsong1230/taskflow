'use client';

import { useState } from 'react';
import type { TaskStatus, TaskPriority } from '@/types/api';
import { taskApi } from '@/lib/api';

interface CreateTaskFormProps {
  projectId: number;
  initialStatus: TaskStatus;
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateTaskForm({
  projectId,
  initialStatus,
  onClose,
  onSuccess,
}: CreateTaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      const newTask = await taskApi.create(projectId, {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
      });

      // 백엔드에서 기본값이 'todo'이므로, initialStatus가 다르면 상태 업데이트
      if (initialStatus !== 'todo') {
        await taskApi.updateStatus(projectId, newTask.id, { status: initialStatus });
      }

      onSuccess();
      onClose();
    } catch (err) {
      console.error('Failed to create task:', err);
      alert('태스크 생성에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-2xl font-bold mb-4">새 태스크 만들기</h2>
        <form onSubmit={handleSubmit}>
          {/* 제목 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              제목 *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="태스크 제목을 입력하세요"
              required
              autoFocus
            />
          </div>

          {/* 설명 */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              설명 (선택사항)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="태스크 설명을 입력하세요"
              rows={3}
            />
          </div>

          {/* 우선순위 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              우선순위
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as TaskPriority)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="low">낮음</option>
              <option value="medium">보통</option>
              <option value="high">높음</option>
              <option value="critical">긴급</option>
            </select>
          </div>

          {/* 초기 상태 표시 */}
          <div className="mb-6 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              초기 상태:{' '}
              <span className="font-medium">
                {initialStatus === 'todo' && 'Todo'}
                {initialStatus === 'in_progress' && 'In Progress'}
                {initialStatus === 'done' && 'Done'}
              </span>
            </p>
          </div>

          {/* 버튼 */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !title.trim()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '만드는 중...' : '만들기'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
