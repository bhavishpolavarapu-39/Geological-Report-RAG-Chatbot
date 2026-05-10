/** @type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Image optimization
  images: {
    unoptimized: process.env.NODE_ENV === 'development',
    formats: ['image/avif', 'image/webp'],
    domains: [
      'localhost',
      'api.example.com',
      'cdn.example.com',
    ],
  },
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    NEXT_PUBLIC_APP_NAME: 'GeoMind AI',
    NEXT_PUBLIC_APP_VERSION: '1.0.0',
  },
  
  // Headers
  headers: async () => [
    {
      source: '/:path*',
      headers: [
        {
          key: 'X-DNS-Prefetch-Control',
          value: 'on'
        },
        {
          key: 'X-Frame-Options',
          value: 'SAMEORIGIN'
        },
        {
          key: 'X-Content-Type-Options',
          value: 'nosniff'
        },
        {
          key: 'X-XSS-Protection',
          value: '1; mode=block'
        },
        {
          key: 'Referrer-Policy',
          value: 'strict-origin-when-cross-origin'
        },
        {
          key: 'Permissions-Policy',
          value: 'camera=(), microphone=(), geolocation=(self)'
        },
      ],
    },
  ],
  
  // Redirects
  redirects: async () => [
    {
      source: '/docs',
      destination: '/documentation',
      permanent: false,
    },
  ],
  
  // Rewrites
  rewrites: async () => ({
    beforeFiles: [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ],
  }),
  
  // TypeScript
  typescript: {
    tsconfigPath: './tsconfig.json',
  },
  
  // Webpack
  webpack: (config, { isServer }) => {
    config.experiments = {
      ...config.experiments,
      asyncIteration: true,
    };
    
    return config;
  },
  
  // Build optimization
  productionBrowserSourceMaps: false,
  generateEtags: true,
  compress: true,
  
  // Performance
  swcMinify: true,
  
  // Output
  output: 'standalone',
  
  // Experimental features
  experimental: {
    optimizeCss: true,
    optimizePackageImports: [
      'recharts',
      'framer-motion',
      'lucide-react',
    ],
  },
};

module.exports = nextConfig;
