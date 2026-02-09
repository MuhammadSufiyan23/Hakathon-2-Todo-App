// /** @type {import('next').NextConfig} */
// const nextConfig = {
//   output: 'standalone', // Enable standalone output for Docker
//   images: {
//     domains: ['lh3.googleusercontent.com', 'avatars.githubusercontent.com'], // For user avatars if using social login
//   },
// };

// module.exports = nextConfig;


/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
}

module.exports = nextConfig
