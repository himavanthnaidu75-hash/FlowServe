import { useToastStore } from '../../store/toastStore';
import { CheckCircle, XCircle, Info } from 'lucide-react';

export const ToastContainer = () => {
  const { toasts, removeToast } = useToastStore();
  return (
    <div className="fixed bottom-4 right-4 z-[100] space-y-2">
      {toasts.map((t) => (
        <div key={t.id} className={`flex items-center gap-2 px-4 py-3 rounded-md shadow-lg border bg-bg-secondary border-border text-white fade-in-up`}>
          {t.type === 'success' && <CheckCircle className="w-5 h-5 text-green-500" />}
          {t.type === 'error' && <XCircle className="w-5 h-5 text-red-500" />}
          {t.type === 'info' && <Info className="w-5 h-5 text-blue-500" />}
          <span className="text-sm">{t.message}</span>
          <button onClick={() => removeToast(t.id)} className="ml-2 text-gray-500 hover:text-white">×</button>
        </div>
      ))}
    </div>
  );
};
