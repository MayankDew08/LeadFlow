import { Inbox, Search } from 'lucide-react';

export default function EmptyState({ hasFilters, onAddLead }) {
  const Icon = hasFilters ? Search : Inbox;
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-200 bg-white px-6 py-12 text-center">
      <Icon className="h-12 w-12 text-gray-300" />
      <p className="mt-4 text-base font-medium text-gray-500">{hasFilters ? 'No leads found' : 'No leads yet'}</p>
      <p className="mt-1 text-sm text-gray-400">{hasFilters ? 'Try adjusting your search or filters' : 'Create your first lead to get started'}</p>
      <button type="button" onClick={onAddLead} className="mt-5 h-10 rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white hover:bg-indigo-700">
        + Add Lead
      </button>
    </div>
  );
}
