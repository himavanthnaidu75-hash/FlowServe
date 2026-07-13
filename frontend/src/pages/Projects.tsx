import { useState } from 'react';
import { useFetch, useCreate } from '../hooks/useData';
import { Plus, Search, AlertCircle, Folder } from 'lucide-react';
import { useToastStore } from '../store/toastStore';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { Modal } from '../components/ui/Modal';
import { formatCurrency, formatDate } from '../lib/utils';

export default function Projects() {
  const [modalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState('');
  const { data: projects, isLoading, isError, refetch } = useFetch<any[]>(['projects'], '/projects');
  const { data: clients } = useFetch<any[]>(['clients'], '/clients');
  const createProject = useCreate<any, any>(['projects'], '/projects');
  const { addToast } = useToastStore();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    try {
      await createProject.mutateAsync({
        name: formData.get('name'),
        client_id: formData.get('client_id'),
        amount: Number(formData.get('amount')),
        deadline: formData.get('deadline') || undefined,
      });
      addToast('Project created', 'success');
      setModalOpen(false);
    } catch {
      addToast('Failed to create project', 'error');
    }
  };

  if (isLoading) return <div className="h-64 skeleton-shimmer rounded-xl"></div>;
  if (isError) return (
    <div className="flex flex-col items-center py-20">
      <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
      <p className="text-gray-500 mb-4">Failed to load projects.</p>
      <button onClick={refetch} className="btn-primary">Retry</button>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold">Projects</h1>
          <p className="text-gray-400 mt-1">Manage all ongoing and completed work.</p>
        </div>
        <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Project
        </button>
      </div>

      <div className="flex items-center gap-2 bg-bg-tertiary border border-border rounded-md px-4 py-2.5 max-w-md">
        <Search className="w-4 h-4 text-gray-500" />
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search projects..." aria-label="Search projects" className="bg-transparent text-sm outline-none w-full" />
      </div>

      {(!projects || projects.length === 0) ? (
        <EmptyState icon={Folder} title="No Projects Yet" message="Start by creating your first project." actionLabel="New Project" onAction={() => setModalOpen(true)} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects?.filter((p: any) => p.name?.toLowerCase().includes(search.toLowerCase())).map((p: any) => (
            <div key={p.id} className="brutalist-card">
              <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-red-900/20 rounded-md">
                  <Folder className="w-5 h-5 text-red-500" />
                </div>
                <StatusBadge status={p.status || 'active'} />
              </div>
              <h3 className="text-lg font-bold mb-1">{p.name}</h3>
              <p className="text-sm text-gray-500 mb-4">{p.client?.name || p.client_id}</p>
              
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Progress</span>
                  <span className="font-mono">{p.progress || 0}%</span>
                </div>
                <div className="h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
                  <div className="h-full bg-red-500" style={{ width: `${p.progress || 0}%` }}></div>
                </div>
              </div>

              <div className="flex justify-between items-center mt-4 pt-4 border-t border-border">
                <div>
                  <p className="text-xs text-gray-500">Budget</p>
                  <p className="text-sm font-mono">{formatCurrency(p.amount || 0)}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Deadline</p>
                  <p className="text-sm font-mono">{p.deadline ? formatDate(p.deadline) : 'N/A'}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Project">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="project-name" className="block text-xs uppercase text-gray-500 mb-2">Project Name</label>
            <input id="project-name" name="name" className="brutalist-input w-full" required />
          </div>
          <div>
            <label htmlFor="project-client" className="block text-xs uppercase text-gray-500 mb-2">Client</label>
            <select id="project-client" name="client_id" className="brutalist-input w-full" required>
              <option value="">Select a client</option>
              {clients?.map((c: any) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="project-budget" className="block text-xs uppercase text-gray-500 mb-2">Budget ($)</label>
            <input id="project-budget" name="amount" type="number" step="0.01" className="brutalist-input w-full" required />
          </div>
          <div>
            <label htmlFor="project-deadline" className="block text-xs uppercase text-gray-500 mb-2">Deadline</label>
            <input id="project-deadline" name="deadline" type="date" className="brutalist-input w-full" />
          </div>
          <div className="flex gap-3 pt-4">
            <button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" className="btn-primary flex-1">Create</button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
