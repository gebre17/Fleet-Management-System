/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Use standalone output for Docker containers; Vercel handles bundling natively
  output: process.env.VERCEL ? undefined : 'standalone',
};

module.exports = nextConfig;

