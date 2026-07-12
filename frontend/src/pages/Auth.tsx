import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { api } from '../lib/api';

export default function Auth() {
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/signup';
      const payload = mode === 'login' ? { email, password } : { email, password, name };
      const { data } = await api.post(endpoint, payload);
      login(data.access_token, data.user);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary p-4">
      <div className="w-full max-w-md">
        <Link to="/" className="block text-center mb-8">
          <div className="text-xl font-display font-extrabold">
            FLOW<span className="text-red-500">SERVE</span>
          </div>
        </Link>
        
        <div className="brutalist-card">
          <div className="flex border-b border-border mb-6">
            <button 
              onClick={() => setMode('login')} 
              className={`flex-1 py-3 text-sm font-bold uppercase tracking-wider transition-colors ${mode === 'login' ? 'border-b-2 border-red-500 text-red-500' : 'text-gray-500'}`}
            >
              Sign In
            </button>
            <button 
              onClick={() => setMode('signup')} 
              className={`flex-1 py-3 text-sm font-bold uppercase tracking-wider transition-colors ${mode === 'signup' ? 'border-b-2 border-red-500 text-red-500' : 'text-gray-500'}`}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'signup' && (
              <div>
                <label htmlFor="name" className="block text-xs uppercase text-gray-500 mb-2">Full Name</label>
                <input id="name" name="name" type="text" value={name} onChange={(e) => setName(e.target.value)} className="brutalist-input" required />
              </div>
            )}
            <div>
              <label htmlFor="email" className="block text-xs uppercase text-gray-500 mb-2">Email</label>
              <input id="email" name="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} className="brutalist-input" required />
            </div>
            <div>
              <label htmlFor="password" className="block text-xs uppercase text-gray-500 mb-2">Password</label>
              <input id="password" name="password" type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} className="brutalist-input" required />
            </div>

            {error && <div className="bg-red-900/20 border border-red-500/30 text-red-400 text-sm p-3 rounded-md">{error}</div>}

            <button type="submit" disabled={loading} className="btn-primary w-full flex justify-center">
              {loading ? 'Processing...' : mode === 'login' ? 'Enter Dashboard' : 'Create Account'}
            </button>
            
            {mode === 'login' && (
              <div className="text-right">
                <Link to="/auth" className="text-xs text-gray-500 hover:text-red-500">Forgot password?</Link>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
