export function LeadSkeletons() {
  return (
    <div className="space-y-2">
      {[1, 2, 3].map((k) => (
        <div key={k} className="h-20 animate-pulse rounded-lg bg-gray-100" />
      ))}
    </div>
  );
}

export function TimelineSkeletons() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((k) => (
        <div key={k} className="flex gap-3">
          <div className="h-3 w-3 rounded-full bg-gray-200" />
          <div className="w-full space-y-2">
            <div className="h-3 w-1/3 animate-pulse rounded bg-gray-100" />
            <div className="h-12 w-full animate-pulse rounded bg-gray-100" />
          </div>
        </div>
      ))}
    </div>
  );
}
