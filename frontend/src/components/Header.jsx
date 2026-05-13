import ProfileMenu from './ProfileMenu';

export default function Header({ onAddLead, user, onLogout }) {
  return (
    <header className="sticky top-0 z-30 h-16 border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-full w-full max-w-4xl items-center justify-between px-4 sm:px-6">
        <h1 className="text-xl font-semibold tracking-tight text-gray-900">⚡ LeadFlow</h1>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onAddLead}
            className="h-10 rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white transition-colors hover:bg-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2"
          >
            + Add Lead
          </button>
          <ProfileMenu user={user} onLogout={onLogout} />
        </div>
      </div>
    </header>
  );
}
