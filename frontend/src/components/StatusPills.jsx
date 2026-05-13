import { STATUS_TABS } from '../store/filterStore';

export default function StatusPills({ status, onChange }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto">
      {STATUS_TABS.map((tab) => {
        const active = tab === status;
        return (
          <button
            key={tab}
            type="button"
            onClick={() => onChange(tab)}
            className={`whitespace-nowrap rounded-full px-3 py-1.5 text-sm transition-colors ${
              active
                ? 'bg-indigo-600 text-white'
                : 'bg-transparent text-gray-600 hover:bg-gray-100'
            }`}
          >
            {tab}
          </button>
        );
      })}
    </div>
  );
}
