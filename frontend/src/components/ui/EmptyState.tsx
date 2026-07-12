import { LucideIcon } from 'lucide-react';

export const EmptyState = ({ icon: Icon, title, message, actionLabel, onAction }: { icon: LucideIcon; title: string; message: string; actionLabel?: string; onAction?: () => void }) => (
  <div className="flex flex-col items-center justify-center py-20 border-2 border-dashed border-border rounded-xl">
    <Icon className="w-12 h-12 text-gray-600 mb-4" />
    <h3 className="text-xl font-bold mb-2">{title}</h3>
    <p className="text-gray-500 mb-6">{message}</p>
    {actionLabel && onAction && <button onClick={onAction} className="btn-primary">{actionLabel}</button>}
  </div>
);
