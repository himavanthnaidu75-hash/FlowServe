import { Link } from 'react-router-dom';
import { ArrowRight, Check, Zap, Shield, Clock, Users, FileText, GitBranch } from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-bg-primary text-white">
      <nav className="absolute top-0 left-0 right-0 z-40 p-6 flex justify-between items-center">
        <div className="text-xl font-display font-extrabold">
          FLOW<span className="text-red-500">SERVE</span>
        </div>
        <div className="flex gap-4">
          <Link to="/auth" className="btn-secondary">Sign In</Link>
          <Link to="/auth" className="btn-primary">Get Started</Link>
        </div>
      </nav>

      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-red-900/10 to-bg-primary"></div>
        <div className="relative z-10 text-center max-w-5xl mx-auto px-6">
          <div className="inline-block mb-6 px-4 py-1.5 border border-red-500/30 bg-red-900/10 rounded-full text-red-400 text-xs font-mono uppercase tracking-widest">
            Field Service Management Reimagined
          </div>
          <h1 className="text-6xl md:text-8xl font-display font-extrabold tracking-tighter leading-none mb-8">
            YOUR WORK.<br />
            YOUR <span className="text-red-500">RULES.</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10">
            Unapologetic power for digital freelancers and agencies. Manage projects, clients, and revenue with brutal efficiency.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/auth" className="btn-primary flex items-center justify-center gap-2">
              Get Started <ArrowRight className="w-4 h-4" />
            </Link>
            <a href="#features" className="btn-secondary">See Features</a>
          </div>
        </div>
      </section>

      <section className="border-y border-border bg-bg-secondary">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4">
          {[
            { num: '100%', label: 'Built for freelancers' },
            { num: 'Open', label: 'Source' },
            { num: 'Self-', label: 'Hostable' },
            { num: 'API-', label: 'First design' },
          ].map((s, i) => (
            <div key={i} className={`p-8 text-center ${i !== 3 ? 'md:border-r border-border' : ''}`}>
              <div className="text-4xl md:text-5xl font-display font-extrabold text-red-500 mb-2">{s.num}</div>
              <div className="text-sm text-gray-500 uppercase tracking-wider">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      <section id="features" className="max-w-7xl mx-auto px-6 py-24">
        <h2 className="text-4xl md:text-5xl font-display font-extrabold mb-12 text-center">
          BUILT FOR <span className="text-red-500">DOMINANCE</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { icon: Zap, title: 'Lightning Projects', desc: 'Create, track, and deliver projects with ruthless precision.' },
            { icon: Users, title: 'Client Command', desc: 'Centralize client data and communication. No more chaos.' },
            { icon: FileText, title: 'Proposals & Invoices', desc: 'Generate high-converting docs and get paid faster.' },
            { icon: Clock, title: 'Time Tracking', desc: 'Every second accounted for. Every hour billable.' },
            { icon: Shield, title: 'Secure Portal', desc: 'Give clients access without compromising control.' },
            { icon: GitBranch, title: 'Team Workflow', desc: 'Assign roles, track progress, scale operations.' },
          ].map((f, i) => (
            <div key={i} className="brutalist-card-interactive">
              <f.icon className="w-8 h-8 text-red-500 mb-4" strokeWidth={1.5} />
              <h3 className="text-xl font-bold mb-2">{f.title}</h3>
              <p className="text-gray-400">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-6 py-24">
        <h2 className="text-4xl md:text-5xl font-display font-extrabold mb-12 text-center">
          CHOOSE YOUR <span className="text-red-500">WEAPON</span>
        </h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            { name: 'Starter', price: '29', desc: 'For solo gunslingers.', features: ['5 Active Projects', 'Basic Time Tracking', '1 User'] },
            { name: 'Professional', price: '79', desc: 'For growing agencies.', features: ['Unlimited Projects', 'Team Collaboration', 'Client Portal', 'API Access'], popular: true },
            { name: 'Enterprise', price: '199', desc: 'For industrial scale.', features: ['Everything in Pro', 'Dedicated Support', 'SSO & Advanced Security', 'Custom Integrations'] },
          ].map((p) => (
            <div key={p.name} className={`brutalist-card relative ${p.popular ? 'border-red-500' : ''}`}>
              {p.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full uppercase">
                  Popular
                </div>
              )}
              <h3 className="text-lg font-bold text-gray-400 uppercase tracking-wider mb-2">{p.name}</h3>
              <div className="flex items-baseline mb-4">
                <span className="text-5xl font-display font-extrabold">${p.price}</span>
                <span className="text-gray-500 ml-2">/mo</span>
              </div>
              <p className="text-gray-400 mb-6">{p.desc}</p>
              <ul className="space-y-3 mb-8">
                {p.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-gray-300">
                    <Check className="w-4 h-4 text-red-500" /> {f}
                  </li>
                ))}
              </ul>
              <Link to="/auth" className={`w-full block text-center ${p.popular ? 'btn-primary' : 'btn-secondary'}`}>
                Start Now
              </Link>
            </div>
          ))}
        </div>
      </section>

      <section className="px-6 py-24">
        <div className="max-w-5xl mx-auto bg-gradient-to-r from-red-900/20 via-red-700/10 to-bg-primary border border-red-500/30 rounded-2xl p-12 text-center">
          <h2 className="text-4xl md:text-5xl font-display font-extrabold mb-4">
            STOP WAITING. START <span className="text-red-500">CONQUERING.</span>
          </h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">Join thousands of freelancers who took control of their business.</p>
          <Link to="/auth" className="btn-primary inline-flex">Create Free Account</Link>
        </div>
      </section>

      <footer className="border-t border-border py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center">
          <div className="text-xl font-display font-extrabold mb-4 md:mb-0">
            FLOW<span className="text-red-500">SERVE</span>
          </div>
          <p className="text-gray-500 text-sm">{new Date().getFullYear()} FlowServe. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
