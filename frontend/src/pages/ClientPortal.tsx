import { useParams } from 'react-router-dom';
import { useFetch } from '../hooks/useData';
import { Folder, CheckCircle, MessageSquare, AlertCircle, Eye } from 'lucide-react';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { useState } from 'react';

export default function ClientPortal() {
  const { token } = useParams();
  const [activeTab, setActiveTab] = useState('overview');
  
  const { data, isLoading, isError } = useFetch<any>(['portal', token], `/portal/${token}`);

  if (!token || isError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-bg-primary p-4">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Invalid or Expired Link</h1>
        <p className="text-gray-500 mb-6">This portal link is no longer active.</p>
        <p className="text-sm text-gray-600">Please contact your service provider.</p>
      </div>
    );
  }

  if (isLoading) return <div className="min-h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500" aria-live="polite"></div></div>;

  const tabs = ['Overview', 'Projects', 'Invoices', 'Messages'];

  return (
    <div className="min-h-screen bg-bg-primary text-white">
      <header className="border-b border-border">
        <div className="max-w-5xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="text-xl font-display font-extrabold">
            FLOW<span className="text-red-500">SERVE</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center text-sm font-bold">
              {data?.client_name?.[0] || 'C'}
            </div>
            <span className="font-medium">{data?.client_name || 'Client'}</span>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-display font-bold mb-8">Welcome, {data?.client_name?.split(' ')[0] || 'Client'}</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="brutalist-card">
            <Folder className="w-5 h-5 text-red-500 mb-2" />
            <h3 className="text-2xl font-bold">{data?.active_projects ?? 0}</h3>
            <p className="text-sm text-gray-500 uppercase">Active Projects</p>
          </div>
          <div className="brutalist-card">
            <CheckCircle className="w-5 h-5 text-green-500 mb-2" />
            <h3 className="text-2xl font-bold">{data?.completed_milestones ?? 0}</h3>
            <p className="text-sm text-gray-500 uppercase">Milestones Done</p>
          </div>
          <div className="brutalist-card">
            <MessageSquare className="w-5 h-5 text-blue-500 mb-2" />
            <h3 className="text-2xl font-bold">{data?.unread_messages ?? 0}</h3>
            <p className="text-sm text-gray-500 uppercase">Unread Messages</p>
          </div>
        </div>

        <div className="flex border-b border-border mb-6">
          {tabs.map((t) => (
            <button key={t} onClick={() => setActiveTab(t.toLowerCase())} className={`px-4 py-2 text-sm font-medium ${activeTab === t.toLowerCase() ? 'border-b-2 border-red-500 text-red-500' : 'text-gray-500'}`}>
              {t}
            </button>
          ))}
        </div>

        {activeTab === 'overview' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold">Current Progress</h2>
            {data?.projects?.map((p: any) => (
              <div key={p.id} className="brutalist-card">
                <div className="flex justify-between mb-2">
                  <h4 className="font-bold">{p.name}</h4>
                  <span className="font-mono text-sm">{p.progress}%</span>
                </div>
                <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
                  <div className="h-full bg-red-500" style={{ width: `${p.progress}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'projects' && (
          <div className="space-y-4">
            {data?.projects?.length === 0 ? (
              <EmptyState icon={Folder} title="No Projects" message="There are no active projects right now." />
            ) : (
              data?.projects?.map((p: any) => (
                <div key={p.id} className="brutalist-card flex justify-between items-center">
                  <div>
                    <h4 className="font-bold">{p.name}</h4>
                    <p className="text-sm text-gray-500">{p.deadline}</p>
                  </div>
                  <StatusBadge status={p.status} />
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'invoices' && (
          <div className="space-y-4">
            {data?.invoices?.length === 0 ? (
              <EmptyState icon={AlertCircle} title="No Invoices" message="You have no invoices yet." />
            ) : (
              data?.invoices?.map((i: any) => (
                <div key={i.id} className="brutalist-card flex justify-between items-center">
                  <div>
                    <h4 className="font-bold font-mono">#{i.number}</h4>
                    <p className="text-sm text-gray-500">${i.amount}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <StatusBadge status={i.status} />
                    <button aria-label="View invoice" className="p-2 hover:bg-bg-tertiary rounded-md"><Eye className="w-4 h-4" /></button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'messages' && (
          <div className="space-y-4">
            {data?.messages?.length === 0 ? (
              <EmptyState icon={MessageSquare} title="No Messages" message="Start a conversation below." />
            ) : (
              data?.messages?.map((m: any) => (
                <div key={m.id} className={`p-4 rounded-lg ${m.unread ? 'bg-red-900/10 border-l-2 border-red-500' : 'bg-bg-secondary'}`}>
                  <p className="text-sm text-gray-300">{m.body}</p>
                  <p className="text-xs text-gray-500 mt-2">{m.author} - {m.timestamp}</p>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  );
}
