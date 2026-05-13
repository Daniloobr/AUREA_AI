import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/request';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value;
  const { pathname } = request.nextUrl;

  // Protected routes
  const protectedPaths = ['/dashboard', '/history', '/generate'];
  const isProtected = protectedPaths.some(path => pathname.startsWith(path));

  // Auth routes (shouldn't be accessible if already logged in)
  const authPaths = ['/login', '/register'];
  const isAuthPath = authPaths.some(path => pathname.startsWith(path));

  if (isProtected && !token) {
    // If trying to access protected route without token, redirect to login
    const url = new URL('/login', request.url);
    return NextResponse.redirect(url);
  }

  if (isAuthPath && token) {
    // If already logged in and trying to access login/register, redirect to dashboard
    const url = new URL('/dashboard', request.url);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/history/:path*', '/generate/:path*', '/login', '/register'],
};
