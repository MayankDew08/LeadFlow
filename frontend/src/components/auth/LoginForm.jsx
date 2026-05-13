import { AlertCircle, Loader2 } from 'lucide-react';
import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import PasswordInput from './PasswordInput';

export default function LoginForm() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const passwordRef = useRef(null);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login.mutateAsync({ email, password });
    } catch (err) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;
      if (status === 401) {
        setError(typeof detail === 'string' ? detail : 'Invalid email or password');
        setPassword('');
        passwordRef.current?.focus();
      } else if (!err?.response) {
        setError('Connection failed. Check your internet.');
      } else {
        setError(typeof detail === 'string' ? detail : 'Something went wrong. Please try again.');
      }
    }
  };

  return (
    <form onSubmit={onSubmit}>
      {error && (
        <div role="alert" className="mb-4 flex items-center gap-2 rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 text-red-500" />
          <span>{error}</span>
        </div>
      )}
      <div className="space-y-4">
        <div>
          <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-gray-700">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            autoComplete="email"
            autoFocus
            disabled={login.isPending}
            className="h-11 w-full rounded-lg border border-gray-200 px-3.5 text-sm transition-colors focus-visible:border-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
          />
        </div>
        <div>
          <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-gray-700">Password</label>
          <PasswordInput
            id="password"
            inputRef={passwordRef}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
            disabled={login.isPending}
          />
        </div>
      </div>
      <button
        type="submit"
        disabled={login.isPending}
        aria-busy={login.isPending}
        className="mt-6 inline-flex h-11 w-full items-center justify-center rounded-lg bg-indigo-600 text-sm font-medium text-white transition-colors hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {login.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Sign in'}
      </button>
      <p className="mt-6 text-center text-sm text-gray-500">
        Don&apos;t have an account?{' '}
        <Link to="/signup" className="font-medium text-indigo-600 hover:text-indigo-700">Sign up</Link>
      </p>
    </form>
  );
}
