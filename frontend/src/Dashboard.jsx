import { useMemo, useState } from 'react';
import AddLeadModal from './components/AddLeadModal';
import ErrorBanner from './components/ErrorBanner';
import FilterBar from './components/FilterBar';
import Header from './components/Header';
import LeadDialog from './components/LeadDialog';
import LeadList from './components/LeadList';
import useDebounce from './hooks/useDebounce';
import { useAuth } from './hooks/useAuth';
import { useCreateLead, useLeads, useTodayFollowUps } from './hooks/useLeads';
import { useFilterStore } from './store/filterStore';

export default function Dashboard() {
  const [selectedLead, setSelectedLead] = useState(null);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const { search, status, setSearch, setStatus } = useFilterStore();
  const debouncedSearch = useDebounce(search, 300);
  const { user, logout } = useAuth();

  const leadsQuery = useLeads({ status, search: debouncedSearch });
  const todayQuery = useTodayFollowUps();
  const createLead = useCreateLead();

  const leads = leadsQuery.data?.leads || [];
  const todayLeads = todayQuery.data?.leads || [];
  const todaySet = useMemo(() => new Set(todayLeads.map((x) => x.id)), [todayLeads]);
  const allLeadsWithoutToday = leads.filter((x) => !todaySet.has(x.id));

  return (
    <div className="flex min-h-full flex-col bg-page text-gray-900">
      <Header onAddLead={() => setIsAddOpen(true)} user={user} onLogout={logout} />
      <FilterBar search={search} onSearch={setSearch} status={status} onStatus={setStatus} />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-6 sm:px-6">
        {(leadsQuery.isError || todayQuery.isError) && (
          <div className="mb-4">
            <ErrorBanner message="Failed to load leads. Please try again." onRetry={() => { leadsQuery.refetch(); todayQuery.refetch(); }} />
          </div>
        )}
        <LeadList
          leads={allLeadsWithoutToday}
          todayLeads={todayLeads}
          loading={leadsQuery.isLoading || todayQuery.isLoading}
          onSelectLead={setSelectedLead}
          onAddLead={() => setIsAddOpen(true)}
          hasFilters={Boolean(search) || status !== 'All'}
        />
      </main>
      <LeadDialog lead={selectedLead} open={Boolean(selectedLead)} onClose={() => setSelectedLead(null)} />
      <AddLeadModal
        open={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        onSubmit={(payload) => createLead.mutate(payload, { onSuccess: () => setIsAddOpen(false) })}
        submitting={createLead.isPending}
      />
    </div>
  );
}
