interface ProgressBarProps {
  total: number;
  completed: number;
  height?: string;
  showLabel?: boolean;
}

export default function ProgressBar({
  total,
  completed,
  height = 'h-4',
  showLabel = true,
}: ProgressBarProps) {
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100);

  return (
    <div>
      <div className={`w-full bg-gray-200 rounded-full ${height} overflow-hidden`}>
        <div
          className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full transition-all duration-500 ease-out flex items-center justify-center"
          style={{ width: `${percentage}%` }}
        >
          {showLabel && percentage > 10 && (
            <span className="text-xs font-semibold text-white">
              {percentage}%
            </span>
          )}
        </div>
      </div>
      {showLabel && percentage <= 10 && (
        <p className="text-xs text-gray-600 mt-1 text-right">
          {completed}/{total} 완료 ({percentage}%)
        </p>
      )}
    </div>
  );
}
