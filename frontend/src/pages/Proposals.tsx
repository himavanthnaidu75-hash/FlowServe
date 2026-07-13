import { useState } from 'react';
import { useFetch, useCreate } from '../hooks/useData';
import { Plus, Search, AlertCircle, FileText, Eye, Download, Send } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useToastStore } from '../store/toastStore';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { formatCurrency, formatDate } from '../lib/utils';

export default function Proposals() {
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState('');
  const { data: proposals, isLoading, isError, refetch } = useFetch<any[]>(['proposals'], '/proposals');
  const { data: clients } = useFetch<any[]>(['clients'], '/clients');
  const createProposal = useCreate<any, any>(['proposals'], '/proposals');
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  const sendProposal = useMutation({
    mutationFn: async (id: string) => await api.post(`/proposals/${id}/send`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proposals'] });
      addToast('Proposal sent');
    },
    onError: () => addToast('Failed to send proposal', 'error'),
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await createProposal.mutateAsync({
        title: fd.get('title'),
        client_id: fd.get('client_id'),
        amount: Number(fd.get('amount')),
      });
      addToast('Proposal created', 'success');
      setModalOpen(false);
    } catch {
      addToast('Failed to create proposal', 'error');
    }
  };

  if (isLoading) return <div className="h-64 skeleton-shimmer rounded-xl"></div>;
  if (isError) return (
    <div className="flex flex-col items-center py-20">
      <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
      <p className="text-gray-500 mb-4">Failed to load proposals.</p>
      <button onClick={refetch} className="btn-primary">Retry</button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold">Proposals</h1>
          <p className="text-gray-400 mt-1">Create and send professional proposals.</p>
        </div>
        <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Proposal
        </button>
      </div>

      <div className="flex items-center gap-2 bg-bg-tertiary border border-border rounded-md px-4 py-2.5 max-w-md">
        <Search className="w-4 h-4 text-gray-500" />
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search proposals..." aria-label="Search proposals" className="bg-transparent text-sm outline-none w-full" />
      </div>

      {(!proposals || proposals.length === 0) ? (
        <EmptyState icon={FileText} title="No Proposals Yet" message="Create your first proposal and send it to a client." actionLabel="New Proposal" onAction={() => setModalOpen(true)} />
      ) : (
        <div className="space-y-3">
          {proposals?.filter((p: any) => p.title?.toLowerCase().includes(search.toLowerCase())).map((p: any) => (
            <div key={p.id} className="brutalist-card flex flex-col md:flex-row items-start md:items-center justify-between gap-4 py-4">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-red-900/20 rounded-md">
                  <FileText className="w-5 h-5 text-red-500" />
                </div>
                <div>
                  <h3 className="font-bold">{p.title}</h3>
                  <p className="text-sm text-gray-500">{p.client?.name || p.client_id}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="font-mono text-sm">{formatCurrency(p.amount || 0)}</p>
                  <p className="text-xs text-gray-500">{p.sent_at ? formatDate(p.sent_at) : 'Draft'}</p>
                </div>
                <StatusBadge status={p.status || 'draft'} />
                <div className="flex gap-1">
                  {p.status === 'draft' && (
                    <button aria-label="Send proposal" onClick={() => sendProposal.mutate(p.id)} className="p-1.5 hover:bg-bg-tertiary rounded"><Send className="w-4 h-4" /></button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Proposal">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label htmlFor="proposal-title" className="block text-xs uppercase text-gray-500 mb-2">Title</label><input id="proposal-title" name="title" className="brutalist-input w-full" required /></div>
          <div>
            <label htmlFor="proposal-client" className="block text-xs uppercase text-gray-500 mb-2">Client</label>
            <select id="proposal-client" name="client_id" className="brutalist-input w-full" required>
              <option value="">Select a client</option>
              {clients?.map((c: any) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div><label htmlFor="proposal-value" className="block text-xs uppercase text-gray-500 mb-2">Amount ($)</label><input id="proposal-value" name="amount" type="number" step="0.01" className="brutalist-input w-full" required /></div>
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" className="btn-primary flex-1">Create</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
