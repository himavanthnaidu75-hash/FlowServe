import { useFetch } from '../hooks/useData';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { Bell, CheckCircle, AlertTriangle, Zap, Trophy, Settings, Check, X, Clock } from 'lucide-react';
import { useToastStore } from '../store/toastStore';
import { EmptyState } from '../components/ui/EmptyState';

const TYPE_CONFIG: Record<string, { icon: any; color: string; bg: string }> = {
  reminder: { icon: Clock, color: 'text-blue-500', bg: 'bg-blue-900/20' },
  alert: { icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-900/20' },
  suggestion: { icon: Zap, color: 'text-yellow-500', bg: 'bg-yellow-900/20' },
  achievement: { icon: Trophy, color: 'text-green-500', bg: 'bg-green-900/20' },
  system: { icon: Settings, color: 'text-gray-500', bg: 'bg-gray-900/20' },
};

export default function Notifications() {
  const { data: notifications, isLoading, refetch } = useFetch<any[]>(['notifications'], '/notifications?limit=100');
  const { data: countData } = useFetch<any>(['notification-count'], '/notifications/count');
  const queryClient = useQueryClient();
  const { addToast } = useToastStore();

  const markRead = useMutation({
    mutationFn: async (id: string) => await api.patch(`/notifications/${id}/read`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications', 'notification-count'] }),
  });

  const markAllRead = useMutation({
    mutationFn: async () => await api.post('/notifications/read-all'),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['notifications', 'notification-count'] }); addToast('All marked as read'); },
  });

  const dismiss = useMutation({
    mutationFn: async (id: string) => await api.patch(`/notifications/${id}/dismiss`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  if (isLoading) return <div className="h-64 skeleton-shimmer rounded-xl"></div>;

  const unread = notifications?.filter((n: any) => !n.is_read && !n.is_dismissed) || [];
  const read = notifications?.filter((n: any) => n.is_read || n.is_dismissed) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-display font-bold">Notifications</h1>
          <p className="text-gray-400 mt-1">
            Smart alerts and suggestions.
            {countData?.unread > 0 && <span className="text-red-500 ml-2 font-mono">{countData.unread} unread</span>}
          </p>
        </div>
        {unread.length > 0 && (
          <button onClick={() => markAllRead.mutate()} className="btn-secondary flex items-center gap-2 text-sm">
            <Check className="w-4 h-4" /> Mark all read
          </button>
        )}
      </div>

      {unread.length === 0 && read.length === 0 ? (
        <EmptyState icon={Bell} title="All caught up" message="No notifications yet. They'll appear here as your business grows." />
      ) : (
        <>
          {unread.length > 0 && (
            <div className="space-y-2">
              <h2 className="text-xs uppercase text-gray-500 font-bold tracking-wider">Unread ({unread.length})</h2>
              {unread.map((n: any) => (
                <NotificationCard key={n.id} notification={n} onRead={() => markRead.mutate(n.id)} onDismiss={() => dismiss.mutate(n.id)} />
              ))}
            </div>
          )}
          {read.length > 0 && (
            <div className="space-y-2">
              <h2 className="text-xs uppercase text-gray-500 font-bold tracking-wider">Earlier</h2>
              {read.slice(0, 20).map((n: any) => (
                <NotificationCard key={n.id} notification={n} onRead={() => markRead.mutate(n.id)} onDismiss={() => dismiss.mutate(n.id)} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function NotificationCard({ notification, onRead, onDismiss }: { notification: any; onRead: () => void; onDismiss: () => void }) {
  const config = TYPE_CONFIG[notification.notification_type] || TYPE_CONFIG.system;
  const Icon = config.icon;

  return (
    <div className={`brutalist-card flex items-start gap-4 py-3 ${
      !notification.is_read && !notification.is_dismissed ? 'border-l-4 border-red-500' : 'opacity-60'
    }`}>
      <div className={`p-2 rounded-lg ${config.bg} shrink-0`}>
        <Icon className={`w-4 h-4 ${config.color}`} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-bold text-sm">{notification.title}</p>
        <p className="text-xs text-gray-500 mt-1 line-clamp-2">{notification.message}</p>
        <div className="flex items-center gap-3 mt-2">
          <span className="text-xs text-gray-600 font-mono">{new Date(notification.created_at).toLocaleDateString()}</span>
          {notification.is_automated && <span className="text-xs bg-yellow-900/20 text-yellow-500 px-1.5 py-0.5 rounded">Auto</span>}
          {notification.action_url && (
            <a href={notification.action_url} className="text-xs text-red-500 hover:underline">{notification.action_label || 'View'} →</a>
          )}
        </div>
      </div>
      <div className="flex gap-1 shrink-0">
        {!notification.is_read && (
          <button onClick={onRead} className="p-1.5 hover:bg-bg-tertiary rounded" title="Mark read">
            <Check className="w-3.5 h-3.5 text-green-500" />
          </button>
        )}
        <button onClick={onDismiss} className="p-1.5 hover:bg-bg-tertiary rounded" title="Dismiss">
          <X className="w-3.5 h-3.5 text-gray-500" />
        </button>
      </div>
    </div>
  );
}
