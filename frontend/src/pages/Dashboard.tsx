import { useFetch } from '../hooks/useData';
import { TrendingUp, Folder, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { formatCurrency } from '../lib/utils';

export default function Dashboard() {
  const { data, isLoading, isError, refetch } = useFetch<any>(['dashboard'], '/dashboard/stats');

  if (isLoading) return <DashboardSkeleton />;
  if (isError) return <ErrorState onRetry={refetch} />;

  const stats = [
    { label: 'Total Revenue', value: data?.total_revenue ? formatCurrency(data.total_revenue) : '$0', change: '+12.5%', icon: TrendingUp },
    { label: 'Active Projects', value: data?.active_projects ?? 0, change: '+3', icon: Folder },
    { label: 'Hours Tracked', value: data?.hours_tracked ?? 0, change: '+24', icon: Clock },
    { label: 'Completed', value: data?.completed_projects ?? 0, change: '+8', icon: CheckCircle },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-display font-bold">Dashboard</h1>
        <p className="text-gray-400 mt-1">Welcome back. Here's what's happening.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="brutalist-card">
            <div className="flex justify-between items-start mb-4">
              <div className="p-2 bg-red-900/20 rounded-md">
                <s.icon className="w-5 h-5 text-red-500" />
              </div>
              <span className="text-xs font-mono text-green-500 bg-green-900/20 px-2 py-1 rounded">{s.change}</span>
            </div>
            <h3 className="text-3xl font-display font-bold">{s.value}</h3>
            <p className="text-sm text-gray-500 uppercase tracking-wider mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 brutalist-card">
          <h3 className="text-lg font-bold mb-6">Revenue Overview</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.revenue_timeline || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" vertical={false} />
                <XAxis dataKey="month" stroke="#525252" />
                <YAxis stroke="#525252" />
                <Tooltip cursor={{ fill: '#1a1a1a' }} contentStyle={{ background: '#111', border: '1px solid #2a2a2a', borderRadius: '4px' }} />
                <Bar dataKey="revenue" fill="#dc2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="brutalist-card">
          <h3 className="text-lg font-bold mb-6">Recent Activity</h3>
          <div className="space-y-4">
            {data?.recent_activity?.map((a: any) => (
              <div key={a.id} className="flex items-start gap-3">
                <div className="w-2 h-2 bg-red-500 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm">{a.message}</p>
                  <p className="text-xs text-gray-500 font-mono">{new Date(a.timestamp).toLocaleTimeString()}</p>
                </div>
              </div>
            )) || <p className="text-sm text-gray-500">No recent activity.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

const DashboardSkeleton = () => (
  <div className="space-y-8">
    <div className="h-10 w-48 skeleton-shimmer rounded"></div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => <div key={i} className="h-32 skeleton-shimmer rounded-xl"></div>)}
    </div>
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 h-80 skeleton-shimmer rounded-xl"></div>
      <div className="h-80 skeleton-shimmer rounded-xl"></div>
    </div>
  </div>
);

const ErrorState = ({ onRetry }: { onRetry: () => void }) => (
  <div className="flex flex-col items-center justify-center py-20">
    <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
    <h3 className="text-xl font-bold mb-2">Connection Failed</h3>
    <p className="text-gray-500 mb-4">Could not fetch dashboard data.</p>
    <button onClick={onRetry} className="btn-primary">Retry</button>
  </div>
);
