// lib/auth-client.ts
// Commenting out Better Auth since we're using custom auth endpoints
// import { createAuthClient } from "better-auth/client";  // <-- ye sahi import hai (remove /react)

// export const authClient = createAuthClient({
//   baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api",
//   // Add other config if needed (e.g. fetch options)
// });

// // Export hooks
// export const { useSession, signIn, signUp, signOut } = authClient;

import { useState, useEffect } from 'react';

// Placeholder exports to avoid breaking existing imports
export const authClient = {
  useSession: () => {
    const [session, setSession] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
      // Get session from localStorage
      if (typeof window !== 'undefined') {
        const storedData = localStorage.getItem('auth');
        if (storedData) {
          try {
            const authData = JSON.parse(storedData);
            setSession({ data: { token: authData.token, user: authData.user }, accessToken: authData.token });
          } catch (e) {
            console.error('Error parsing auth data from localStorage:', e);
            setSession(null);
          }
        } else {
          setSession(null);
        }
      }
      setIsLoading(false);
    }, []);

    return { data: session, isLoading };
  },
  signIn: { email: async () => {} },
  signUp: { email: async () => {} },
  signOut: async () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth');
    }
    return { data: null, error: null };
  }
};

export const { useSession, signIn, signUp, signOut } = authClient;