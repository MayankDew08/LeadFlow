import { AlertCircle, Loader2 } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import PasswordInput from './PasswordInput';

export default function SignupForm() {
  const { signup } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [touched, setTouched] = useState({});

  const errors = useMemo(() => {
    const next = {};
    if (!name.trim()) next.name = 'Name is required';
    if (!email.trim()) next.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) next.email = 'Please enter a valid email';
    if (!password) next.password = 'Password is required';
    else if (password.length < 6) next.password = 'Password must be at least 6 characters';
    return next;
  }, [name, email, password]);

  const submit = async (e) => {
    e.preventDefault();
    setTouched({ name: true, email: true, password: true });
    setError('');
    if (Object.keys(errors).length) return;
    try {
      await signup.mutateAsync({ name: name.trim(), email, password });
    } catch (err) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;
      if (status === 400) {
        setError(typeof detail === 'string' ? detail : 'An account with this email already exists');
      } else if (status === 422) {
        setError('Submitted data is invalid. Please check all fields.');
      } else if (!err?.response) {
        setError('Connection failed. Check your internet.');
      } else {
        setError(typeof detail === 'string' ? detail : 'Something went wrong. Please try again.');
      }
    }
  };

  return (
    <form onSubmit={submit}>
      {error && (
        <div role="alert" className="mb-4 flex items-center gap-2 rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span>{error}</span>
        </div>
      )}
      <div className="space-y-4">
        <div>
          <label htmlFor="name" className="mb-1.5 block text-sm font-medium text-gray-700">Full name</label>
          <input id="name" value={name} onBlur={() => setTouched((v) => ({ ...v, name: true }))} onChange={(e) => setName(e.target.value)} autoFocus autoComplete="name" placeholder="John Doe" className="h-11 w-full rounded-lg border border-gray-200 px-3.5 text-sm focus-visible:border-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20" />
          {touched.name && errors.name && <p className="mt-1.5 text-xs text-red-500">{errors.name}</p>}
        </div>
        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-gray-700">Email</label>
          <input id="email" type="email" value={email} onBlur={() => setTouched((v) => ({ ...v, email: true }))} onChange={(e) => setEmail(e.target.value)} autoComplete="email" placeholder="you@company.com" className="h-11 w-full rounded-lg border border-gray-200 px-3.5 text-sm focus-visible:border-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20" />
          {touched.email && errors.email && <p className="mt-1.5 text-xs text-red-500">{errors.email}</p>}
        </div>
        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-gray-700">Password</label>
          <PasswordInput id="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" autoComplete="new-password" />
          <p className="mt-1.5 text-xs text-gray-500">Must be at least 6 characters</p>
          {touched.password && errors.password && <p className="mt-1.5 text-xs text-red-500">{errors.password}</p>}
        </div>
      </div>
      <button
        type="submit"
        disabled={signup.isPending}
        aria-busy={signup.isPending}
        className="mt-6 inline-flex h-11 w-full items-center justify-center rounded-lg bg-indigo-600 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {signup.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create account'}
      </button>
      <p className="mt-6 text-center text-sm text-gray-500">
        Already have an account?{' '}
        <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-700">Sign in</Link>
      </p>
    </form>
  );
}
