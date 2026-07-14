import { useFetch } from '../hooks/useData';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Users, FileText, Clock, Target, AlertCircle, Zap, ArrowUpRight, ArrowDownRight, DollarSign, Briefcase } from 'lucide-react';
import { formatCurrency } from '../lib/utils';

const COLORS = ['#dc2626', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];

export default function Analytics() {
  const { data: overview, isLoading: loadingOverview } = useFetch<any>(['analytics-overview'], '/analytics/overview');
  const { data: forecast, isLoading: loadingForecast } = useFetch<any>(['analytics-forecast'], '/analytics/forecast');
  const { data: insights, isLoading: loadingInsights } = useFetch<any>(['analytics-insights'], '/analytics/insights');

  if (loadingOverview || loadingForecast || loadingInsights) return <div className="h-64 skeleton-shimmer rounded-xl"></div>;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-display font-bold">Business Analytics</h1>
        <p className="text-gray-400 mt-1">AI-powered insights and revenue forecasting.</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard icon={DollarSign} label="This Month" value={formatCurrency(overview?.revenue?.this_month || 0)} change={overview?.revenue?.growth_rate} />
        <MetricCard icon={TrendingUp} label="Outstanding" value={formatCurrency(overview?.revenue?.outstanding || 0)} />
        <MetricCard icon={Briefcase} label="Active Projects" value={overview?.projects?.active || 0} />
        <MetricCard icon={Users} label="Total Clients" value={overview?.clients?.total || 0} />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard icon={Target} label="Proposal Win Rate" value={`${overview?.proposals?.acceptance_rate || 0}%`} />
        <MetricCard icon={Clock} label="Utilization" value={`${overview?.time?.utilization || 0}%`} />
        <MetricCard icon={Users} label="Active Leads" value={overview?.clients?.active_leads || 0} />
        <MetricCard icon={DollarSign} label="6-Month Forecast" value={formatCurrency(forecast?.total_forecast_6m || 0)} />
      </div>

      {/* Revenue Trend + Forecast */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="brutalist-card">
          <h3 className="text-lg font-bold mb-4">Revenue Trend</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={overview?.revenue_trend || []}>
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
          <h3 className="text-lg font-bold mb-4">6-Month Forecast</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={forecast?.forecast || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" vertical={false} />
                <XAxis dataKey="month" stroke="#525252" />
                <YAxis stroke="#525252" />
                <Tooltip cursor={{ fill: '#1a1a1a' }} contentStyle={{ background: '#111', border: '1px solid #2a2a2a', borderRadius: '4px' }} />
                <Line type="monotone" dataKey="estimated" stroke="#dc2626" strokeWidth={2} dot={{ fill: '#dc2626' }} />
                <Line type="monotone" dataKey="low" stroke="#525252" strokeWidth={1} strokeDasharray="5 5" dot={false} />
                <Line type="monotone" dataKey="high" stroke="#525252" strokeWidth={1} strokeDasharray="5 5" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Insights */}
      {insights?.insights?.length > 0 && (
        <div className="brutalist-card">
          <div className="flex items-center gap-2 mb-4"><Zap className="w-5 h-5 text-yellow-500" /><h3 className="text-lg font-bold">Smart Insights</h3></div>
          <div className="space-y-3">
            {insights.insights.map((insight: any, i: number) => (
              <div key={i} className={`flex items-start gap-4 p-4 rounded-lg border ${
                insight.priority === 'high' ? 'border-red-500/30 bg-red-900/10' :
                insight.priority === 'medium' ? 'border-yellow-500/30 bg-yellow-900/10' :
                'border-border'
              }`}>
                <div className={`p-2 rounded ${
                  insight.priority === 'high' ? 'bg-red-900/20 text-red-500' :
                  insight.priority === 'medium' ? 'bg-yellow-900/20 text-yellow-500' :
                  'bg-bg-tertiary text-gray-400'
                }`}>
                  {insight.type === 'financial' && <DollarSign className="w-4 h-4" />}
                  {insight.type === 'efficiency' && <Clock className="w-4 h-4" />}
                  {insight.type === 'sales' && <FileText className="w-4 h-4" />}
                  {insight.type === 'growth' && <TrendingUp className="w-4 h-4" />}
                </div>
                <div className="flex-1">
                  <p className="font-bold text-sm">{insight.title}</p>
                  <p className="text-xs text-gray-500 mt-1">{insight.description}</p>
                </div>
                {insight.action_url && (
                  <a href={insight.action_url} className="text-xs text-red-500 hover:underline whitespace-nowrap">{insight.action} →</a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Time Breakdown */}
      <div className="brutalist-card">
        <h3 className="text-lg font-bold mb-4">Time Tracking Summary</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold">{overview?.time?.total_hours || 0}h</p>
            <p className="text-xs text-gray-500 uppercase">Total Hours</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-500">{overview?.time?.billable_hours || 0}h</p>
            <p className="text-xs text-gray-500 uppercase">Billable Hours</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-red-500">{overview?.time?.utilization || 0}%</p>
            <p className="text-xs text-gray-500 uppercase">Utilization Rate</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, label, value, change }: { icon: any; label: string; value: any; change?: number }) {
  return (
    <div className="brutalist-card">
      <div className="flex items-center gap-2 mb-2">
        <div className="p-2 bg-red-900/20 rounded-md"><Icon className="w-4 h-4 text-red-500" /></div>
        {change !== undefined && change !== 0 && (
          <span className={`text-xs font-mono flex items-center gap-0.5 ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            {Math.abs(change)}%
          </span>
        )}
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
    </div>
  );
}
