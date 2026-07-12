import { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

export const Modal = ({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: React.ReactNode }) => {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
      const handleEsc = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
      window.addEventListener('keydown', handleEsc);
      return () => {
        document.body.style.overflow = 'auto';
        window.removeEventListener('keydown', handleEsc);
      };
    }
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" onClick={onClose}>
      <div 
        ref={dialogRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="bg-bg-secondary border border-border rounded-xl p-6 w-full max-w-md outline-none fade-in-scale"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-display font-bold">{title}</h2>
          <button onClick={onClose} aria-label="Close dialog" className="p-2 hover:bg-bg-tertiary rounded-md">
            <X className="w-5 h-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
};
