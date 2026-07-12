import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Menu, Search, Bell } from 'lucide-react';
import { NavPanel } from './NavPanel';

export const AppShell = () => {
  const [navOpen, setNavOpen] = useState(false);
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
            <button aria-label="Notifications" className="relative p-2 hover:bg-bg-tertiary rounded-md transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
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
