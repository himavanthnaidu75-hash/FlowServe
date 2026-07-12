import { useState, useEffect } from 'react';
import { useFetch, useCreate } from '../hooks/useData';
import { Play, StopCircle, Plus, Clock, AlertCircle } from 'lucide-react';
import { formatCurrency } from '../lib/utils';
import { Modal } from '../components/ui/Modal';
import { EmptyState } from '../components/ui/EmptyState';
import { useToastStore } from '../store/toastStore';

export default function TimeTracking() {
  const [isRunning, setIsRunning] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [modalOpen, setModalOpen] = useState(false);
  const { data: entries, isLoading, isError, refetch } = useFetch<any[]>(['time'], '/time-entries');
  const createTime = useCreate<any, any>(['time'], '/time-entries');
  const { addToast } = useToastStore();

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isRunning) {
      interval = setInterval(() => setElapsed(e => e + 1), 1000);
    }
    return () => clearInterval(interval);
  }, [isRunning]);

  const formatTime = (s: number) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  };

  const handleStop = async () => {
    setIsRunning(false);
    if (elapsed > 0) {
      await createTime.mutateAsync({ project: 'Manual', description: 'Timer session', duration: Math.round(elapsed / 60) });
      addToast('Time logged successfully');
    }
    setElapsed(0);
  };

  const totalHours = entries?.reduce((acc, e) => acc + e.duration, 0) || 0;
  const totalAmount = entries?.reduce((acc, e) => acc + e.amount, 0) || 0;

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
          <h1 className="text-3xl font-display font-bold">Time Tracking</h1>
          <p className="text-gray-400 mt-1">Total: <span className="text-red-500 font-mono">{totalHours >= 60 ? `${Math.floor(totalHours / 60)}h ${totalHours % 60}m` : `${totalHours}m`}</span> | Billable: <span className="text-red-500 font-mono">{formatCurrency(totalAmount)}</span></p>
        </div>
        <button onClick={() => setModalOpen(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Log Time
        </button>
      </div>

      <div className="brutalist-card flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className={`p-4 rounded-full ${isRunning ? 'bg-red-500 animate-pulse' : 'bg-bg-tertiary'}`}>
            <Clock className={`w-8 h-8 ${isRunning ? 'text-white' : 'text-red-500'}`} />
          </div>
          <div>
            <h3 className="text-sm uppercase tracking-wider text-gray-500">Current Timer</h3>
            <p className="text-4xl font-mono font-bold">{formatTime(elapsed)}</p>
          </div>
        </div>
        {!isRunning ? (
          <button onClick={() => setIsRunning(true)} className="btn-primary flex items-center gap-2">
            <Play className="w-5 h-5" /> Start
          </button>
        ) : (
          <button onClick={handleStop} className="btn-secondary border-red-500 text-red-500 flex items-center gap-2">
            <StopCircle className="w-5 h-5" /> Stop & Save
          </button>
        )}
      </div>

      <div className="space-y-4">
        {entries?.length === 0 ? (
          <EmptyState icon={Clock} title="No Time Entries" message="Start a timer or log time manually." actionLabel="Log Time" onAction={() => setModalOpen(true)} />
        ) : (
          entries?.map((e) => (
            <div key={e.id} className="brutalist-card flex flex-col md:flex-row justify-between items-start md:items-center gap-4 py-4">
              <div>
                <h4 className="font-bold">{e.description || 'Unnamed Task'}</h4>
                <p className="text-sm text-gray-500">{e.project || 'General'}</p>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-xs text-gray-500 uppercase">Duration</p>
                  <p className="font-mono">{e.duration}m</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500 uppercase">Amount</p>
                  <p className="font-mono text-red-500">{formatCurrency(e.amount || 0)}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Log Time">
        <form onSubmit={async (e) => { e.preventDefault(); const f = new FormData(e.currentTarget); await createTime.mutateAsync({ project: f.get('project'), description: f.get('description'), duration: Number(f.get('duration')) }); addToast('Time logged successfully'); setModalOpen(false); }} className="space-y-4">
          <div><label htmlFor="proj" className="block text-xs uppercase text-gray-500 mb-2">Project</label><input id="proj" name="project" className="brutalist-input" required /></div>
          <div><label htmlFor="desc" className="block text-xs uppercase text-gray-500 mb-2">Description</label><input id="desc" name="description" className="brutalist-input" required /></div>
          <div><label htmlFor="dur" className="block text-xs uppercase text-gray-500 mb-2">Duration (min)</label><input id="dur" name="duration" type="number" className="brutalist-input" required /></div>
          <div className="flex gap-3 pt-4"><button type="button" onClick={() => setModalOpen(false)} className="btn-secondary flex-1">Cancel</button><button type="submit" className="btn-primary flex-1">Log</button></div>
        </form>
      </Modal>
    </div>
  );
}
