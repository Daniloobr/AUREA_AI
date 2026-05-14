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
      }
    ],
  },
  async rewrites() {
    const isDev = process.env.NODE_ENV === 'development';
    if (!isDev) return [];
    
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:5000/api/:path*'
      },
      {
        source: '/uploads/:path*',
        destination: 'http://127.0.0.1:5000/uploads/:path*'
      }
    ];
  }
};

export default nextConfig;
