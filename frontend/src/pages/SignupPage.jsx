import SignupForm from '../components/auth/SignupForm';
import AuthLayout from '../components/auth/AuthLayout';

export default function SignupPage() {
  return (
    <AuthLayout title="Create your account" subtitle="Start managing leads in minutes">
      <SignupForm />
    </AuthLayout>
  );
}
