export const StatusBadge = ({ status }: { status: string }) => {
  const map: Record<string, string> = {
    draft: 'bg-gray-800 text-gray-400',
    sent: 'bg-blue-900/30 text-blue-400',
    viewed: 'bg-indigo-900/30 text-indigo-400',
    accepted: 'bg-green-900/30 text-green-400',
    rejected: 'bg-red-900/30 text-red-400',
    expired: 'bg-yellow-900/30 text-yellow-400',
    active: 'bg-green-900/30 text-green-400',
    paused: 'bg-gray-800 text-gray-400',
    completed: 'bg-blue-900/30 text-blue-400',
    paid: 'bg-green-900/30 text-green-400',
    pending: 'bg-yellow-900/30 text-yellow-400',
    overdue: 'bg-red-900/30 text-red-400',
    void: 'bg-gray-800 text-gray-400',
  };
  return (
    <span className={`text-xs px-2 py-1 rounded font-mono uppercase tracking-wider ${map[status?.toLowerCase()] || 'bg-gray-800 text-gray-400'}`}>
      {status || 'Unknown'}
    </span>
  );
};
