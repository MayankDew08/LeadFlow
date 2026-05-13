import SearchInput from './SearchInput';
import StatusPills from './StatusPills';

export default function FilterBar({ search, onSearch, status, onStatus }) {
  return (
    <div className="sticky top-16 z-20 h-auto border-b border-gray-200 bg-gray-50/80 backdrop-blur">
      <div className="mx-auto flex max-w-4xl flex-col gap-3 px-4 py-2 sm:px-6 md:h-12 md:flex-row md:items-center md:justify-between md:gap-4 md:py-0">
        <SearchInput value={search} onChange={onSearch} />
        <StatusPills status={status} onChange={onStatus} />
      </div>
    </div>
  );
}
