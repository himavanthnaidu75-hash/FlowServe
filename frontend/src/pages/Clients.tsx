import { useState } from 'react';
import { useFetch, useCreate } from '../hooks/useData';
import { Plus, Search, AlertCircle, Users, Mail, Phone, MapPin } from 'lucide-react';
import { useToastStore } from '../store/toastStore';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { formatCurrency } from '../lib/utils';

export default function Clients() {
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState('');
  const { data: clients, isLoading, isError, refetch } = useFetch<any[]>(['clients'], '/clients');
  const createClient = useCreate<any, any>(['clients'], '/clients');
  const { addToast } = useToastStore();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await createClient.mutateAsync({
        name: fd.get('name'),
        email: fd.get('email'),
        phone: fd.get('phone'),
      });
      addToast('Client added', 'success');
      setModalOpen(false);
    } catch {
      addToast('Failed to add client', 'error');
    }
  };

  if (isLoading) return <div className="h-64 skeleton-shimmer rounded-xl"></div>;
  if (isError) return (
    <div className="flex flex-col items-center py-20">
      <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
      <p className="text-gray-500 mb-4">Failed to load clients.</p>
      <button onClick={refetch} className="btn-primary">Retry</button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold">Clients</h1>
          <p className="text-gray-400 mt-1">Manage your client relationships.</p>
        </div>
        <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Add Client
        </button>
      </div>

      <div className="flex items-center gap-2 bg-bg-tertiary border border-border rounded-md px-4 py-2.5 max-w-md">
        <Search className="w-4 h-4 text-gray-500" />
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search clients..." aria-label="Search clients" className="bg-transparent text-sm outline-none w-full" />
      </div>

      {(!clients || clients.length === 0) ? (
        <EmptyState icon={Users} title="No Clients Yet" message="Add your first client to get started." actionLabel="Add Client" onAction={() => setModalOpen(true)} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {clients?.filter((c: any) => c.name?.toLowerCase().includes(search.toLowerCase())).map((c: any) => (
            <div key={c.id} className="brutalist-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-red-900/30 rounded-full flex items-center justify-center text-lg font-bold text-red-500">
                  {c.name?.charAt(0) || '?'}
                </div>
                <div>
                  <h3 className="font-bold">{c.name}</h3>
                  <StatusBadge status={c.status || 'active'} />
                </div>
              </div>
              <div className="space-y-2 text-sm text-gray-400">
                <div className="flex items-center gap-2"><Mail className="w-3.5 h-3.5" /> {c.email}</div>
                <div className="flex items-center gap-2"><Phone className="w-3.5 h-3.5" /> {c.phone || '-'}</div>
                {c.location && <div className="flex items-center gap-2"><MapPin className="w-3.5 h-3.5" /> {c.location}</div>}
              </div>
              <div className="flex justify-between items-center mt-4 pt-4 border-t border-border text-sm">
                <span className="text-gray-500">{c.total_projects || 0} projects</span>
                <span className="font-mono text-red-500">{formatCurrency(c.total_revenue || 0)}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Add Client">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label htmlFor="client-name" className="block text-xs uppercase text-gray-500 mb-2">Name</label><input id="client-name" name="name" className="brutalist-input w-full" required /></div>
          <div><label htmlFor="client-email" className="block text-xs uppercase text-gray-500 mb-2">Email</label><input id="client-email" name="email" type="email" className="brutalist-input w-full" required /></div>
          <div><label htmlFor="client-phone" className="block text-xs uppercase text-gray-500 mb-2">Phone</label><input id="client-phone" name="phone" className="brutalist-input w-full" /></div>
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" className="btn-primary flex-1">Add</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
