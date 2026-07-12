import { useState, useEffect } from 'react';
import { User, Users, Bell, Shield, Palette, CreditCard, KeyRound } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useThemeStore } from '../store/themeStore';
import { useToastStore } from '../store/toastStore';

export default function Settings() {
  const [activeTab, setActiveTab] = useState('profile');
  const { addToast } = useToastStore();
  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'team', label: 'Team', icon: Users },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'billing', label: 'Billing', icon: CreditCard },
    { id: 'api', label: 'API Keys', icon: KeyRound },
  ];

  return (
    <div className="space-y-6">
      <div><h1 className="text-3xl font-display font-bold">Settings</h1><p className="text-gray-400 mt-1">Manage your account and preferences.</p></div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <nav className="space-y-1">
          {tabs.map((t) => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} className={`w-full flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium transition-colors ${activeTab === t.id ? 'bg-red-900/20 text-red-500 border-l-2 border-red-500' : 'text-gray-400 hover:bg-bg-tertiary'}`}>
              <t.icon className="w-4 h-4" /> {t.label}
            </button>
          ))}
        </nav>

        <div className="lg:col-span-3 brutalist-card relative">
          {activeTab === 'profile' && <ProfileForm />}
          {activeTab === 'api' && <ApiKeys addToast={addToast} />}
          {activeTab === 'team' && <TeamBillingDemo addToast={addToast} title="Team Management" />}
          {activeTab === 'billing' && <TeamBillingDemo addToast={addToast} title="Billing History" />}
          {activeTab === 'notifications' && <NotificationsSettings addToast={addToast} />}
          {activeTab === 'security' && <SecuritySettings addToast={addToast} />}
          {activeTab === 'appearance' && <AppearanceSettings />}
        </div>
      </div>
    </div>
  );
}

const ProfileForm = () => {
  const { user } = useAuthStore();
  const { addToast } = useToastStore();
  return (
    <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); addToast('Profile updated successfully'); }}>
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 bg-red-500 rounded-full flex items-center justify-center text-2xl font-bold">{user?.name?.[0] || 'U'}</div>
        <button type="button" onClick={() => addToast('Avatar upload coming soon')} className="btn-secondary">Change Avatar</button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div><label htmlFor="name" className="block text-xs uppercase text-gray-500 mb-2">Name</label><input id="name" defaultValue={user?.name || ''} className="brutalist-input" /></div>
        <div><label htmlFor="email" className="block text-xs uppercase text-gray-500 mb-2">Email</label><input id="email" defaultValue={user?.email || ''} className="brutalist-input" /></div>
      </div>
      <button type="submit" className="btn-primary">Save Changes</button>
    </form>
  );
};

const ApiKeys = ({ addToast }: { addToast: (m: string) => void }) => (
  <div className="space-y-4">
    <div className="absolute top-4 right-4 text-xs bg-bg-tertiary text-gray-500 px-2 py-1 rounded">Demo data — wire to API</div>
    <div className="flex justify-between items-center">
      <h3 className="text-lg font-bold">API Keys</h3>
      <button onClick={() => addToast('API Key generated')} className="btn-primary">Generate Key</button>
    </div>
    <div className="border border-border rounded-md p-4 flex justify-between items-center">
      <div>
        <p className="font-mono text-sm">sk_live_...4f2a</p>
        <p className="text-xs text-gray-500 mt-1">Last used: 2 days ago</p>
      </div>
      <button onClick={() => addToast('API Key revoked')} className="text-red-500 text-sm hover:underline">Revoke</button>
    </div>
  </div>
);

const TeamBillingDemo = ({ addToast, title }: { addToast: (m: string) => void; title: string }) => (
  <div className="space-y-4">
    <div className="absolute top-4 right-4 text-xs bg-bg-tertiary text-gray-500 px-2 py-1 rounded">Demo data — wire to API</div>
    <h3 className="text-lg font-bold">{title}</h3>
    <button onClick={() => addToast('Action triggered')} className="btn-primary">Add New</button>
    <div className="border border-border rounded-md p-4">No items found.</div>
  </div>
);

const NotificationsSettings = ({ addToast }: { addToast: (m: string) => void }) => {
  const [email, setEmail] = useState(true);
  const [push, setPush] = useState(false);
  const [reports, setReports] = useState(true);

  const Toggle = ({ enabled, setEnabled, label }: { enabled: boolean; setEnabled: (v: boolean) => void; label: string }) => (
    <div className="flex items-center justify-between py-3 border-b border-border">
      <span>{label}</span>
      <button 
        type="button"
        role="switch" 
        aria-checked={enabled} 
        onClick={() => { setEnabled(!enabled); addToast('Notification preference updated'); }}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary ${enabled ? 'bg-red-500' : 'bg-bg-tertiary'}`}
      >
        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${enabled ? 'translate-x-6' : 'translate-x-1'}`} />
      </button>
    </div>
  );

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold">Notifications</h3>
      <Toggle enabled={email} setEnabled={setEmail} label="Email Notifications" />
      <Toggle enabled={push} setEnabled={setPush} label="Push Notifications" />
      <Toggle enabled={reports} setEnabled={setReports} label="Weekly Reports" />
    </div>
  );
};

const SecuritySettings = ({ addToast }: { addToast: (m: string) => void }) => (
  <div className="space-y-6">
    <h3 className="text-lg font-bold">Security</h3>
    <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); addToast('Password updated'); }}>
      <div><label htmlFor="curr" className="block text-xs uppercase text-gray-500 mb-2">Current Password</label><input id="curr" type="password" className="brutalist-input" /></div>
      <div><label htmlFor="new" className="block text-xs uppercase text-gray-500 mb-2">New Password</label><input id="new" type="password" className="brutalist-input" /></div>
      <button type="submit" className="btn-primary">Update Password</button>
    </form>
    <div className="pt-6 border-t border-border">
      <button onClick={() => addToast('2FA flow initiated')} className="btn-secondary">Enable 2FA</button>
    </div>
  </div>
);

const AppearanceSettings = () => {
  const { color, setColor } = useThemeStore();
  const colors = [
    { name: 'Red', value: '#dc2626' },
    { name: 'Blue', value: '#3b82f6' },
    { name: 'Green', value: '#10b981' },
    { name: 'Yellow', value: '#eab308' },
  ];

  useEffect(() => {
    document.documentElement.style.setProperty('--theme-color', color);
  }, [color]);

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-bold">Appearance</h3>
      <div>
        <label className="block text-xs uppercase text-gray-500 mb-4">Theme Color</label>
        <div className="flex gap-4">
          {colors.map((c) => (
            <button 
              key={c.value} 
              onClick={() => setColor(c.value)} 
              aria-label={`Set theme to ${c.name}`}
              className={`w-10 h-10 rounded-full transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary ${color === c.value ? 'ring-2 ring-white' : ''}`} 
              style={{ backgroundColor: c.value }} 
            />
          ))}
        </div>
      </div>
    </div>
  );
};
