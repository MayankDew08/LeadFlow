import LeadCard from './LeadCard';
import EmptyState from './EmptyState';
import { LeadSkeletons } from './LoadingSkeletons';

export default function LeadList({ leads, todayLeads, loading, onSelectLead, onAddLead, hasFilters }) {
  if (loading) return <LeadSkeletons />;
  if (!leads.length) return <EmptyState hasFilters={hasFilters} onAddLead={onAddLead} />;

  return (
    <div className="space-y-8">
      {todayLeads.length > 0 && (
        <section>
          <div className="mb-3 flex items-center gap-2">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">Today&apos;s Follow-ups</h3>
            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700">{todayLeads.length}</span>
          </div>
          <div className="space-y-2">
            {todayLeads.map((lead) => (
              <LeadCard key={lead.id} lead={lead} onClick={() => onSelectLead(lead)} />
            ))}
          </div>
        </section>
      )}
      <section>
        <div className="mb-3 flex items-center gap-2">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-500">All Leads</h3>
          <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">{leads.length}</span>
        </div>
        <div className="space-y-2">
          {leads.map((lead) => (
            <LeadCard key={lead.id} lead={lead} onClick={() => onSelectLead(lead)} />
          ))}
        </div>
      </section>
    </div>
  );
}
