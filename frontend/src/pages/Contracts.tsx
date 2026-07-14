import { useState } from 'react';
import { useFetch, useCreate, useDelete } from '../hooks/useData';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Plus, AlertCircle, FileText, Trash2, Eye, Edit, Download } from 'lucide-react';
import { useToastStore } from '../store/toastStore';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { formatCurrency, formatDate } from '../lib/utils';

const TEMPLATES = [
  { value: 'service_agreement', label: 'Service Agreement' },
  { value: 'sow', label: 'Statement of Work' },
  { value: 'nda', label: 'Non-Disclosure Agreement' },
  { value: 'change_order', label: 'Change Order' },
];

export default function Contracts() {
  const [modalOpen, setModalOpen] = useState(false);
  const [viewContract, setViewContract] = useState<any>(null);
  const { data: contracts, isLoading, isError, refetch } = useFetch<any[]>(['contracts'], '/contracts');
  const { data: clients } = useFetch<any[]>(['clients'], '/clients');
  const createContract = useCreate<any, any>(['contracts'], '/contracts');
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  const deleteContract = useMutation({
    mutationFn: async (id: string) => await api.delete(`/contracts/${id}`),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['contracts'] }); addToast('Contract deleted'); },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await createContract.mutateAsync({
        client_id: fd.get('client_id'),
        title: fd.get('title'),
        contract_type: fd.get('contract_type'),
        total_value: Number(fd.get('total_value')) || 0,
        variables: {
          client_name: clients?.find((c: any) => c.id === fd.get('client_id'))?.name || '',
          scope_description: fd.get('scope') || '',
        },
      });
      addToast('Contract generated', 'success');
      setModalOpen(false);
    } catch { addToast('Failed to create contract', 'error'); }
  };

  if (isLoading) return <div className="h-64 skeleton-shimmer rounded-xl"></div>;
  if (isError) return <div className="flex flex-col items-center py-20"><AlertCircle className="w-12 h-12 text-red-500 mb-4" /><button onClick={refetch} className="btn-primary">Retry</button></div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold">Contracts</h1>
          <p className="text-gray-400 mt-1">Auto-generated contracts, SOWs, and NDAs.</p>
        </div>
        <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> New Contract</button>
      </div>

      {contracts?.length === 0 ? (
        <EmptyState icon={FileText} title="No Contracts" message="Generate professional contracts from templates." actionLabel="New Contract" onAction={() => setModalOpen(true)} />
      ) : (
        <div className="space-y-3">
          {contracts?.map((c: any) => (
            <div key={c.id} className="brutalist-card flex flex-col md:flex-row items-start md:items-center justify-between gap-4 py-4">
              <div className="flex items-center gap-4">
                <div className="p-2 bg-red-900/20 rounded-md"><FileText className="w-5 h-5 text-red-500" /></div>
                <div>
                  <h3 className="font-bold">{c.title}</h3>
                  <p className="text-sm text-gray-500">{TEMPLATES.find(t => t.value === c.contract_type)?.label || c.contract_type}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right hidden md:block">
                  <p className="font-mono text-sm">{c.total_value > 0 ? formatCurrency(c.total_value) : '-'}</p>
                  <p className="text-xs text-gray-500">{formatDate(c.created_at)}</p>
                </div>
                <StatusBadge status={c.status} />
                <div className="flex gap-1">
                  <button onClick={() => setViewContract(c)} className="p-1.5 hover:bg-bg-tertiary rounded"><Eye className="w-4 h-4" /></button>
                  <button onClick={() => { if (confirm('Delete?')) deleteContract.mutate(c.id); }} className="p-1.5 hover:bg-bg-tertiary rounded"><Trash2 className="w-4 h-4 text-gray-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Contract">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs uppercase text-gray-500 mb-2">Client *</label>
            <select name="client_id" className="brutalist-input w-full" required>
              <option value="">Select client</option>
              {clients?.map((c: any) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div><label className="block text-xs uppercase text-gray-500 mb-2">Title *</label><input name="title" className="brutalist-input w-full" required /></div>
          <div>
            <label className="block text-xs uppercase text-gray-500 mb-2">Type *</label>
            <select name="contract_type" className="brutalist-input w-full" required>
              {TEMPLATES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div><label className="block text-xs uppercase text-gray-500 mb-2">Value ($)</label><input name="total_value" type="number" step="0.01" className="brutalist-input w-full" /></div>
          <div><label className="block text-xs uppercase text-gray-500 mb-2">Scope Description</label><textarea name="scope" className="brutalist-input w-full" rows={4} placeholder="Describe the project scope..." /></div>
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" className="btn-primary flex-1">Generate</button>
          </div>
        </form>
      </Modal>

      <Modal open={!!viewContract} onClose={() => setViewContract(null)} title={viewContract?.title || 'Contract'}>
        {viewContract && (
          <div className="prose prose-invert prose-sm max-w-none">
            <pre className="whitespace-pre-wrap text-sm text-gray-300 leading-relaxed">{viewContract.content}</pre>
            <div className="flex gap-3 pt-6 mt-6 border-t border-border">
              <button onClick={() => setViewContract(null)} className="btn-secondary flex-1">Close</button>
              <button onClick={() => { navigator.clipboard.writeText(viewContract.content); addToast('Copied to clipboard'); }} className="btn-primary flex-1">Copy Text</button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
