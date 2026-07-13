import { useState } from 'react';
import { useFetch, useCreate } from '../hooks/useData';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, AlertCircle, Download, Send, Receipt, Trash2 } from 'lucide-react';
import { api } from '../lib/api';
import { Modal } from '../components/ui/Modal';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { useToastStore } from '../store/toastStore';
import { formatCurrency, formatDate } from '../lib/utils';

export default function Invoices() {
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState('');
  const { data: invoices, isLoading, isError, refetch } = useFetch<any[]>(['invoices'], '/invoices');
  const { data: clients } = useFetch<any[]>(['clients'], '/clients');
  const createInvoice = useCreate<any, any>(['invoices'], '/invoices');
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  const deleteInvoice = useMutation({
    mutationFn: async (id: string) => await api.delete(`/invoices/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      addToast('Invoice deleted');
    },
  });

  const remindInvoice = useMutation({
    mutationFn: async (id: string) => await api.post(`/invoices/${id}/remind`),
    onSuccess: () => addToast('Reminder sent'),
    onError: () => addToast('Failed to send reminder', 'error'),
  });

  if (isLoading) return <div className="h-64 skeleton-shimmer rounded-xl"></div>;
  if (isError) return (
    <div className="flex flex-col items-center py-20">
      <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
      <button onClick={refetch} className="btn-primary">Retry</button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold">Invoices</h1>
          <p className="text-gray-400 mt-1">Outstanding: <span className="text-red-500 font-mono">{formatCurrency(invoices?.filter(i => i.status === 'pending' || i.status === 'overdue').reduce((acc, i) => acc + i.amount, 0) || 0)}</span></p>
        </div>
        <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Invoice
        </button>
      </div>

      <div className="flex items-center gap-2 bg-bg-tertiary border border-border rounded-md px-4 py-2.5 max-w-md">
        <Search className="w-4 h-4 text-gray-500" />
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search invoices..." className="bg-transparent text-sm outline-none w-full" />
      </div>

      {invoices?.length === 0 ? (
        <EmptyState icon={Receipt} title="No Invoices Yet" message="Start by creating your first invoice." actionLabel="New Invoice" onAction={() => setModalOpen(true)} />
      ) : (
        <div className="space-y-3">
          {invoices?.filter(i => (i.number || '').toLowerCase().includes(search.toLowerCase()) || (i.client_id || '').toLowerCase().includes(search.toLowerCase())).map((i) => (
            <div key={i.id} className="brutalist-card flex flex-col md:flex-row justify-between items-start md:items-center gap-4 py-4">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-bg-tertiary rounded-md">
                  <Receipt className="w-5 h-5 text-red-500" />
                </div>
                <div>
                  <h4 className="font-bold font-mono">#{i.number}</h4>
                  <p className="text-sm text-gray-500">{i.client_id}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right hidden md:block">
                  <p className="text-xs text-gray-500 uppercase">Amount</p>
                  <p className="font-mono">{formatCurrency(i.amount)}</p>
                </div>
                <div className="text-right hidden md:block">
                  <p className="text-xs text-gray-500 uppercase">Due</p>
                  <p className="font-mono">{formatDate(i.due_date)}</p>
                </div>
                <StatusBadge status={i.status} />
                <div className="flex gap-2">
                  {i.status === 'pending' && (
                    <button aria-label="Send reminder" onClick={() => remindInvoice.mutate(i.id)} className="p-2 hover:bg-bg-tertiary rounded-md" title="Send reminder"><Send className="w-4 h-4" /></button>
                  )}
                  <button aria-label="Delete invoice" onClick={() => { if (confirm('Delete this invoice?')) deleteInvoice.mutate(i.id); }} className="p-2 hover:bg-bg-tertiary rounded-md text-red-500"><Trash2 className="w-4 h-4" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Invoice">
        <form onSubmit={async (e) => { e.preventDefault(); const f = new FormData(e.currentTarget); const amount = Number(f.get('amount')); await createInvoice.mutateAsync({ client_id: f.get('client_id'), due_date: f.get('due_date'), line_items: [{ description: 'Invoice total', quantity: 1, price: amount }] }); addToast('Invoice created successfully'); setModalOpen(false); }} className="space-y-4">
          <div>
            <label htmlFor="client" className="block text-xs uppercase text-gray-500 mb-2">Client</label>
            <select id="client" name="client_id" className="brutalist-input w-full" required>
              <option value="">Select a client</option>
              {clients?.map((c: any) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div><label htmlFor="amount" className="block text-xs uppercase text-gray-500 mb-2">Amount ($)</label><input id="amount" name="amount" type="number" step="0.01" className="brutalist-input" required /></div>
          <div><label htmlFor="due" className="block text-xs uppercase text-gray-500 mb-2">Due Date</label><input id="due" name="due_date" type="date" className="brutalist-input" required /></div>
          <div className="flex gap-3 pt-4"><button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button><button type="submit" className="btn-primary flex-1">Create</button></div>
        </form>
      </Modal>
    </div>
  );
}
