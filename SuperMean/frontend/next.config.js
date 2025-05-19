/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/SuperMean/' : '', // Replace 'SuperMean' with your repo name
  images: {
    unoptimized: true,
  },
}

module.exports = nextConfig