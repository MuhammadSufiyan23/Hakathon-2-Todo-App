'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { fadeInUp } from '@/lib/animations';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';

export default function SigninPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const validateForm = () => {
    const newErrors: typeof errors = {};

    if (!email) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) newErrors.email = 'Email is invalid';

    if (!password) newErrors.password = 'Password is required';
    else if (password.length < 8) newErrors.password = 'Password must be at least 8 characters';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);

    try {
      await apiClient.login(email, password);

      toast.success('Successfully signed in!');
      router.push('/dashboard');
    } catch (error: any) {
      console.error('Signin error:', error);
      toast.error(error.message || 'Invalid email or password');
      setErrors({ password: 'Invalid email or password' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 via-indigo-950 to-purple-950 p-4">
      <motion.div className="w-full max-w-md" initial="hidden" animate="visible" variants={fadeInUp}>
        <Card className="bg-black/40 backdrop-blur-md border border-white/10 shadow-2xl rounded-2xl overflow-hidden">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Welcome Back
            </CardTitle>
            <p className="text-gray-300 mt-2">Sign in to manage your tasks</p>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-200">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`bg-black/20 border-gray-700 text-white placeholder:text-gray-500 ${
                    errors.email ? 'border-red-500' : 'focus:border-indigo-500 focus:ring-indigo-500'
                  }`}
                  placeholder="name@example.com"
                />
                {errors.email && <motion.p className="text-sm text-red-500" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                  {errors.email}
                </motion.p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-200">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`bg-black/20 border-gray-700 text-white placeholder:text-gray-500 ${
                    errors.password ? 'border-red-500' : 'focus:border-indigo-500 focus:ring-indigo-500'
                  }`}
                  placeholder="••••••••"
                />
                {errors.password && <motion.p className="text-sm text-red-500" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
                  {errors.password}
                </motion.p>}
              </div>

              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-300 scale-100 hover:scale-105"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-gray-400">
              Don't have an account?{' '}
              <Link href="/auth/signup" className="font-semibold text-indigo-400 hover:text-indigo-300 hover:underline transition-all duration-200">
                Sign up
              </Link>
            </div>

            <div className="mt-4 text-center text-sm text-gray-400">
              <Link href="#" className="font-semibold text-indigo-400 hover:text-indigo-300 hover:underline transition-all duration-200">
                Forgot password?
              </Link>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}