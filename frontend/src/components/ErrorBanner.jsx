import { AlertCircle } from 'lucide-react';

export default function ErrorBanner({ message, onRetry }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      <div className="flex items-center gap-2">
        <AlertCircle className="h-4 w-4" />
        <span>{message}</span>
        {onRetry && (
          <button type="button" className="ml-auto underline" onClick={onRetry}>
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
