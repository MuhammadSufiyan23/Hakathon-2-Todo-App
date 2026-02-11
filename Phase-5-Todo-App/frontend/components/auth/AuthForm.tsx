'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useFormValidation } from '@/hooks/use-form-validation';
import { Button } from '@/components/ui/button';
import { bounceButton } from '@/lib/animations';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AuthFormProps {
  type: 'signin' | 'signup';
  onSubmit: (formData: { email: string; password: string; confirmPassword?: string }) => void;
  loading?: boolean;
}

export function AuthForm({ type, onSubmit, loading = false }: AuthFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
  });
  const { errors, validateForm, resetErrors } = useFormValidation();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Reset error for this field when user starts typing
    if (errors[name]) {
      resetErrors();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Define validation rules
    const emailRules = [
      { rule: (val: string) => val.length > 0, message: 'Email is required' },
      { rule: (val: string) => /\S+@\S+\.\S+/.test(val), message: 'Email is invalid' },
    ];

    const passwordRules = [
      { rule: (val: string) => val.length >= 8, message: 'Password must be at least 8 characters' },
    ];

    const confirmPasswordRules = type === 'signup' ? [
      { rule: (val: string) => val === formData.password, message: 'Passwords do not match' },
    ] : [];

    const fieldRules = {
      email: emailRules,
      password: passwordRules,
      confirmPassword: confirmPasswordRules,
    };

    // Validate the form
    const isValid = validateForm(formData, fieldRules as any);

    if (isValid) {
      onSubmit(formData);
    }
  };

  // Validation rules for each field
  const emailRules = [
    { rule: (val: string) => val.length > 0, message: 'Email is required' },
    { rule: (val: string) => /\S+@\S+\.\S+/.test(val), message: 'Email is invalid' },
  ];

  const passwordRules = [
    { rule: (val: string) => val.length >= 8, message: 'Password must be at least 8 characters' },
  ];

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="space-y-2">
        <label htmlFor="email" className="text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          className={cn(
            'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
            'ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium',
            'placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2',
            'focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed',
            'disabled:opacity-50',
            errors.email && 'border-red-500 focus-visible:ring-red-500'
          )}
          placeholder="name@example.com"
        />
        {errors.email && (
          <motion.p
            className="text-sm text-red-500"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            {errors.email}
          </motion.p>
        )}
      </div>

      <div className="space-y-2">
        <label htmlFor="password" className="text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          name="password"
          type="password"
          value={formData.password}
          onChange={handleChange}
          className={cn(
            'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
            'ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium',
            'placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2',
            'focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed',
            'disabled:opacity-50',
            errors.password && 'border-red-500 focus-visible:ring-red-500'
          )}
          placeholder="••••••••"
        />
        {errors.password && (
          <motion.p
            className="text-sm text-red-500"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            {errors.password}
          </motion.p>
        )}
      </div>

      {type === 'signup' && (
        <div className="space-y-2">
          <label htmlFor="confirmPassword" className="text-sm font-medium">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={handleChange}
            className={cn(
              'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
              'ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium',
              'placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2',
              'focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed',
              'disabled:opacity-50',
              errors.confirmPassword && 'border-red-500 focus-visible:ring-red-500'
            )}
            placeholder="••••••••"
          />
          {errors.confirmPassword && (
            <motion.p
              className="text-sm text-red-500"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              {errors.confirmPassword}
            </motion.p>
          )}
        </div>
      )}

      <motion.div
        variants={bounceButton}
        whileHover="hover"
        whileTap="tap"
      >
        <Button
          type="submit"
          className={cn(
            'w-full bg-gradient-primary text-white',
            'before:absolute before:inset-0 before:rounded-md before:bg-gradient-primary',
            'before:bg-[length:200%_200%] before:transition-all before:duration-500',
            'hover:before:animate-[shine_1s_linear_infinite]',
            'relative overflow-hidden'
          )}
          disabled={loading}
        >
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : null}
          {type === 'signin' ? 'Sign In' : 'Sign Up'}
        </Button>
      </motion.div>
    </motion.form>
  );
}