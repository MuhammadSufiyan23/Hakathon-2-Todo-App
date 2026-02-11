'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from '@/lib/auth-client';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function ProtectedRoute({ children, fallback = null }: ProtectedRouteProps) {
  const { data: session, isLoading } = useSession(); // Destructure session data and loading state
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !session) {
      router.push('/auth/signin');
    }
  }, [session, isLoading, router]);

  if (isLoading) {
    // Show a loading state while checking auth
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (!session) {
    return <>{fallback}</>; // This shouldn't happen due to the redirect above, but just in case
  }

  return <>{children}</>;
}