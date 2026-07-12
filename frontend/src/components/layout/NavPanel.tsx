import { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { X, LayoutDashboard, FolderKanban, Users, FileText, Receipt, Clock, Settings, LogOut } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/projects', label: 'Projects', icon: FolderKanban },
  { to: '/clients', label: 'Clients', icon: Users },
  { to: '/proposals', label: 'Proposals', icon: FileText },
  { to: '/invoices', label: 'Invoices', icon: Receipt },
  { to: '/time', label: 'Time Tracking', icon: Clock },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export const NavPanel = ({ open, onClose }: { open: boolean; onClose: () => void }) => {
  const { user, logout } = useAuthStore();

  useEffect(() => {
    if (open) {
      const handleEsc = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
      window.addEventListener('keydown', handleEsc);
      document.body.style.overflow = 'hidden';
      return () => {
        window.removeEventListener('keydown', handleEsc);
        document.body.style.overflow = 'auto';
      };
    }
  }, [open, onClose]);

  return (
    <div className={`fixed inset-0 z-50 ${open ? 'visible' : 'invisible'}`}>
      <div className={`absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity duration-300 ${open ? 'opacity-100' : 'opacity-0'}`} onClick={onClose}></div>
      <div 
        role="dialog"
        aria-modal="true"
        aria-label="Main navigation"
        className={`absolute top-0 left-0 h-full w-80 bg-bg-secondary border-r border-border p-6 flex flex-col transition-transform duration-300 ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex justify-between items-center mb-12">
          <div className="text-xl font-display font-extrabold">
            FLOW<span className="text-red-500">SERVE</span>
          </div>
          <button onClick={onClose} aria-label="Close menu" className="p-2 hover:bg-bg-tertiary rounded-md transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <nav className="flex-1 space-y-2">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} onClick={onClose} className={({ isActive }) => `flex items-center gap-3 px-4 py-3 rounded-md font-medium transition-all border-l-2 ${isActive ? 'bg-red-900/20 text-red-500 border-red-500' : 'text-gray-400 border-transparent hover:bg-bg-tertiary hover:text-white'}`}>
              <item.icon className="w-5 h-5" /> {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-border pt-4 mt-4">
          <div className="px-4 py-2 mb-2">
            <p className="text-sm font-medium text-white">{user?.name || 'User'}</p>
            <p className="text-xs text-gray-500">{user?.email}</p>
          </div>
          <button onClick={() => { logout(); window.location.href = '/auth'; }} className="w-full flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-red-500 hover:bg-bg-tertiary rounded-md transition-colors">
            <LogOut className="w-5 h-5" /> Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};
