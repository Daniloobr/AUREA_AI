import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
      {
        protocol: 'https',
        hostname: 'replicate.delivery',
      },
      {
        protocol: 'https',
        hostname: '*.supabase.co',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      }
    ],
  },
  async rewrites() {
    const isDev = process.env.NODE_ENV === 'development';
    if (!isDev) return [];
    
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:5005/api/:path*'
      },
      {
        source: '/uploads/:path*',
        destination: 'http://127.0.0.1:5005/uploads/:path*'
      }
    ];
  }
};

export default nextConfig;
