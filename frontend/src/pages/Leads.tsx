import { useState } from 'react';
import { useFetch, useCreate, useUpdate, useDelete } from '../hooks/useData';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Plus, Search, AlertCircle, Target, TrendingUp, ArrowRight, Trash2, Zap, Star, Phone, Mail, Globe } from 'lucide-react';
import { useToastStore } from '../store/toastStore';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { formatCurrency } from '../lib/utils';

const STAGES = [
  { id: 'new', label: 'New', color: 'bg-blue-500' },
  { id: 'contacted', label: 'Contacted', color: 'bg-yellow-500' },
  { id: 'qualified', label: 'Qualified', color: 'bg-purple-500' },
  { id: 'proposal_sent', label: 'Proposal Sent', color: 'bg-orange-500' },
  { id: 'negotiating', label: 'Negotiating', color: 'bg-cyan-500' },
  { id: 'won', label: 'Won', color: 'bg-green-500' },
  { id: 'lost', label: 'Lost', color: 'bg-gray-500' },
];

const SOURCES = ['manual', 'website', 'referral', 'job_board', 'cold_outreach', 'inbound'];
const TYPES = ['web_design', 'web_development', 'mobile_app', 'consulting', 'branding', 'marketing'];
const URGENCY = ['low', 'normal', 'high', 'urgent'];

export default function Leads() {
  const [modalOpen, setModalOpen] = useState(false);
  const [view, setView] = useState<'board' | 'list'>('board');
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState('');
  const { data: leads, isLoading, isError, refetch } = useFetch<any[]>(['leads'], '/leads');
  const { data: pipeline } = useFetch<any>(['pipeline'], '/leads/pipeline/summary');
  const { data: suggestions } = useFetch<any>(['lead-suggestions'], '/leads/suggestions');
  const createLead = useCreate<any, any>(['leads'], '/leads');
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  const convertLead = useMutation({
    mutationFn: async (id: string) => (await api.post(`/leads/${id}/convert`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      addToast('Lead converted to client!');
    },
  });

  const deleteLead = useMutation({
    mutationFn: async (id: string) => await api.delete(`/leads/${id}`),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['leads'] }); addToast('Lead deleted'); },
  });

  const updateStage = useMutation({
    mutationFn: async ({ id, stage }: { id: string; stage: string }) => (await api.patch(`/leads/${id}`, { stage })).data,
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['leads'] }); queryClient.invalidateQueries({ queryKey: ['pipeline'] }); },
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    try {
      await createLead.mutateAsync({
        name: fd.get('name'),
        email: fd.get('email') || undefined,
        company: fd.get('company') || undefined,
        phone: fd.get('phone') || undefined,
        website: fd.get('website') || undefined,
        description: fd.get('description') || undefined,
        source: fd.get('source') || 'manual',
        estimated_budget: Number(fd.get('estimated_budget')) || 0,
        project_type: fd.get('project_type') || undefined,
        urgency: fd.get('urgency') || 'normal',
      });
      addToast('Lead created & scored', 'success');
      setModalOpen(false);
    } catch { addToast('Failed to create lead', 'error'); }
  };

  if (isLoading) return <div className="h-64 skeleton-shimmer rounded-xl"></div>;
  if (isError) return <div className="flex flex-col items-center py-20"><AlertCircle className="w-12 h-12 text-red-500 mb-4" /><button onClick={refetch} className="btn-primary">Retry</button></div>;

  const filteredLeads = leads?.filter((l: any) =>
    (!stageFilter || l.stage === stageFilter) &&
    (l.name.toLowerCase().includes(search.toLowerCase()) || (l.company || '').toLowerCase().includes(search.toLowerCase()))
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold">Lead Pipeline</h1>
          <p className="text-gray-400 mt-1">Discover, score, and convert leads into clients.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setView(view === 'board' ? 'list' : 'board')} className="btn-secondary text-sm">{view === 'board' ? 'List View' : 'Board View'}</button>
          <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-2"><Plus className="w-4 h-4" /> Add Lead</button>
        </div>
      </div>

      {/* Pipeline Summary */}
      {pipeline && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          {STAGES.map(s => (
            <div key={s.id} className="brutalist-card py-3 px-3 text-center">
              <div className={`w-2 h-2 ${s.color} rounded-full mx-auto mb-1`}></div>
              <p className="text-lg font-bold">{pipeline.stages?.[s.id]?.count || 0}</p>
              <p className="text-xs text-gray-500 uppercase">{s.label}</p>
              {pipeline.stages?.[s.id]?.total_value > 0 && (
                <p className="text-xs font-mono text-red-500 mt-1">{formatCurrency(pipeline.stages[s.id].total_value)}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* AI Suggestions */}
      {suggestions?.suggestions?.length > 0 && (
        <div className="brutalist-card border-l-4 border-yellow-500">
          <div className="flex items-center gap-2 mb-2"><Zap className="w-4 h-4 text-yellow-500" /><h3 className="font-bold text-sm uppercase">Smart Suggestions</h3></div>
          <div className="space-y-2">
            {suggestions.suggestions.map((s: any, i: number) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span><strong>{s.lead_name}</strong>: {s.reason}</span>
                <button onClick={() => updateStage.mutate({ id: s.lead_id, stage: s.suggested_stage })} className="text-xs text-yellow-500 hover:underline">Move to {s.suggested_stage.replace('_', ' ')}</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-3">
        <div className="flex items-center gap-2 bg-bg-tertiary border border-border rounded-md px-4 py-2.5 flex-1 max-w-md">
          <Search className="w-4 h-4 text-gray-500" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search leads..." className="bg-transparent text-sm outline-none w-full" />
        </div>
        <select value={stageFilter} onChange={e => setStageFilter(e.target.value)} className="brutalist-input text-sm">
          <option value="">All Stages</option>
          {STAGES.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
        </select>
      </div>

      {filteredLeads.length === 0 ? (
        <EmptyState icon={Target} title="No Leads Yet" message="Start adding leads to build your pipeline." actionLabel="Add Lead" onAction={() => setModalOpen(true)} />
      ) : view === 'board' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredLeads.map((l: any) => (
            <div key={l.id} className="brutalist-card">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${STAGES.find(s => s.id === l.stage)?.color || 'bg-gray-500'}`}></div>
                  <StatusBadge status={l.stage.replace('_', ' ')} />
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-xs font-mono bg-red-900/20 text-red-500 px-2 py-0.5 rounded">{l.score}/100</span>
                  <button onClick={() => { if (confirm('Delete?')) deleteLead.mutate(l.id); }} className="p-1 hover:bg-bg-tertiary rounded"><Trash2 className="w-3 h-3 text-gray-500" /></button>
                </div>
              </div>
              <h3 className="font-bold mb-1">{l.name}</h3>
              {l.company && <p className="text-sm text-gray-500 mb-2">{l.company}</p>}
              {l.estimated_budget > 0 && <p className="text-sm font-mono text-red-500 mb-2">{formatCurrency(l.estimated_budget)}</p>}
              <div className="flex gap-1 flex-wrap mb-3">
                {l.tags?.map((t: string) => <span key={t} className="text-xs bg-bg-tertiary px-2 py-0.5 rounded">{t}</span>)}
                {l.project_type && <span className="text-xs bg-red-900/20 text-red-500 px-2 py-0.5 rounded">{l.project_type.replace('_', ' ')}</span>}
              </div>
              <div className="flex gap-2 text-xs text-gray-500">
                {l.email && <Mail className="w-3 h-3" />}
                {l.phone && <Phone className="w-3 h-3" />}
                {l.website && <Globe className="w-3 h-3" />}
              </div>
              <div className="flex gap-2 mt-3 pt-3 border-t border-border">
                {l.stage !== 'won' && l.stage !== 'lost' && (
                  <>
                    <select onChange={e => { if (e.target.value) updateStage.mutate({ id: l.id, stage: e.target.value }); }} className="brutalist-input text-xs flex-1 py-1">
                      <option value="">Move to...</option>
                      {STAGES.filter(s => s.id !== l.stage).map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                    </select>
                    {l.stage !== 'won' && l.score >= 60 && (
                      <button onClick={() => convertLead.mutate(l.id)} className="text-xs text-green-500 hover:underline whitespace-nowrap">Convert</button>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredLeads.map((l: any) => (
            <div key={l.id} className="brutalist-card flex items-center gap-4 py-3">
              <div className={`w-2 h-2 rounded-full ${STAGES.find(s => s.id === l.stage)?.color}`}></div>
              <div className="flex-1 min-w-0">
                <p className="font-bold truncate">{l.name}</p>
                <p className="text-xs text-gray-500">{l.company || l.source}</p>
              </div>
              <span className="text-xs font-mono bg-red-900/20 text-red-500 px-2 py-0.5 rounded">{l.score}</span>
              <p className="text-sm font-mono">{l.estimated_budget > 0 ? formatCurrency(l.estimated_budget) : '-'}</p>
              <StatusBadge status={l.stage.replace('_', ' ')} />
              <div className="flex gap-1">
                {l.stage !== 'won' && l.stage !== 'lost' && (
                  <select onChange={e => { if (e.target.value) updateStage.mutate({ id: l.id, stage: e.target.value }); }} className="brutalist-input text-xs py-1">
                    <option value="">Move</option>
                    {STAGES.filter(s => s.id !== l.stage).map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                  </select>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Add Lead">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div><label className="block text-xs uppercase text-gray-500 mb-2">Name *</label><input name="name" className="brutalist-input w-full" required /></div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs uppercase text-gray-500 mb-2">Email</label><input name="email" type="email" className="brutalist-input w-full" /></div>
            <div><label className="block text-xs uppercase text-gray-500 mb-2">Phone</label><input name="phone" className="brutalist-input w-full" /></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs uppercase text-gray-500 mb-2">Company</label><input name="company" className="brutalist-input w-full" /></div>
            <div><label className="block text-xs uppercase text-gray-500 mb-2">Website</label><input name="website" className="brutalist-input w-full" /></div>
          </div>
          <div><label className="block text-xs uppercase text-gray-500 mb-2">Description</label><textarea name="description" className="brutalist-input w-full" rows={3} /></div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs uppercase text-gray-500 mb-2">Source</label><select name="source" className="brutalist-input w-full">{SOURCES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}</select></div>
            <div><label className="block text-xs uppercase text-gray-500 mb-2">Project Type</label><select name="project_type" className="brutalist-input w-full"><option value="">Select...</option>{TYPES.map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}</select></div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><label className="block text-xs uppercase text-gray-500 mb-2">Budget ($)</label><input name="estimated_budget" type="number" step="0.01" className="brutalist-input w-full" /></div>
            <div><label className="block text-xs uppercase text-gray-500 mb-2">Urgency</label><select name="urgency" className="brutalist-input w-full">{URGENCY.map(u => <option key={u} value={u}>{u}</option>)}</select></div>
          </div>
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" className="btn-primary flex-1">Create & Score</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
