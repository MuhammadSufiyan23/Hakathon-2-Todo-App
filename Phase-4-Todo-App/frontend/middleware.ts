import { NextRequest, NextResponse } from 'next/server';
import { isTokenExpired } from '@/utils/session';

// Middleware to protect routes
export function middleware(request: NextRequest) {
  // Allow public routes
  const publicRoutes = ['/auth/signin', '/auth/signup'];
  const isPublicRoute = publicRoutes.some(route =>
    request.nextUrl.pathname.startsWith(route)
  );

  // If it's a public route, allow access
  if (isPublicRoute) {
    return NextResponse.next();
  }

  // For protected routes, check authentication
  if (request.nextUrl.pathname.startsWith('/dashboard') ||
      request.nextUrl.pathname.startsWith('/tasks')) {

    // Check for auth token in localStorage (would be handled on the client side)
    // For server-side checking, we'd need to implement server-side session management
    // For now, we'll allow access to these routes but the client-side auth check will handle protection

    // We'll also need to handle auth checking on the client-side in components
    // since localStorage is only accessible in the browser
  }

  return NextResponse.next();
}

// Specify which paths the middleware should run for
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};