import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Menu, Search, Bell } from 'lucide-react';
import { NavPanel } from './NavPanel';
import { useFetch } from '../../hooks/useData';

export const AppShell = () => {
  const [navOpen, setNavOpen] = useState(false);
  const { data: countData } = useFetch<any>(['notification-count'], '/notifications/count');

  return (
    <div className="min-h-screen bg-bg-primary">
      <header className="sticky top-0 z-40 border-b border-border bg-bg-primary/80 backdrop-blur-md">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <button onClick={() => setNavOpen(true)} aria-label="Open menu" aria-expanded={navOpen} className="p-2 hover:bg-bg-tertiary rounded-md transition-colors">
              <Menu className="w-6 h-6" />
            </button>
            <div className="text-xl font-display font-extrabold hidden sm:block">
              FLOW<span className="text-red-500">SERVE</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 bg-bg-tertiary border border-border rounded-md px-4 py-2 w-64">
              <Search className="w-4 h-4 text-gray-500" />
              <input placeholder="Search..." className="bg-transparent text-sm outline-none w-full" />
            </div>
            <a href="/notifications" aria-label="Notifications" className="relative p-2 hover:bg-bg-tertiary rounded-md transition-colors">
              <Bell className="w-5 h-5" />
              {countData?.unread > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] bg-red-500 rounded-full flex items-center justify-center text-[10px] font-bold text-white px-1">
                  {countData.unread > 99 ? '99+' : countData.unread}
                </span>
              )}
            </a>
          </div>
        </div>
      </header>
      <NavPanel open={navOpen} onClose={() => setNavOpen(false)} />
      <main className="p-6 md:p-8 max-w-7xl mx-auto">
        <Outlet />
      </main>
    </div>
  );
};
