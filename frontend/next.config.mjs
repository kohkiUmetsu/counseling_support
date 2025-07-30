/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
  // WebSocket用のカスタムサーバー設定も追加可能
  experimental: {
    proxyTimeout: 30000,
  },
};

export default nextConfig;
