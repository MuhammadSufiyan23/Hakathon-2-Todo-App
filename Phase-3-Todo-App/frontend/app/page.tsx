'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Shield, Zap, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  const features = [
    {
      icon: <Shield className="h-10 w-10 text-indigo-400" />,
      title: "Secure Authentication",
      description: "Enterprise-grade security with JWT authentication and encrypted data storage."
    },
    {
      icon: <Zap className="h-10 w-10 text-yellow-400" />,
      title: "Lightning Fast",
      description: "Optimized for speed with real-time updates and instant task management."
    },
    {
      icon: <CheckCircle className="h-10 w-10 text-emerald-400" />,
      title: "Persistent Tasks",
      description: "Your tasks are safely stored and synchronized across all your devices."
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950 to-purple-950 text-white">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          className="text-center max-w-4xl mx-auto"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Hero Section */}
          <motion.div variants={itemVariants} className="mb-12">
            <motion.h1
              className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                TodoSphere
              </span>
            </motion.h1>
            <motion.p
              className="text-xl md:text-2xl text-gray-300 mb-8 max-w-2xl mx-auto"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              The most beautiful and intuitive task management experience
            </motion.p>
            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <Button asChild size="lg" className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold px-8 py-6 text-lg shadow-lg hover:shadow-xl transition-all duration-300 scale-100 hover:scale-105">
                <Link href="/auth/signup">
                  Get Started Free
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="border-white/30 text-white hover:bg-white/10 font-semibold px-8 py-6 text-lg transition-all duration-300 scale-100 hover:scale-105">
                <Link href="/auth/signin">
                  Sign In
                </Link>
              </Button>
            </motion.div>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            className="grid md:grid-cols-3 gap-8 mb-16"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="bg-black/30 backdrop-blur-md border border-white/10 rounded-2xl p-8 hover:scale-105 transition-all duration-300 hover:shadow-2xl"
                variants={itemVariants}
                whileHover={{ y: -5 }}
              >
                <div className="flex flex-col items-center text-center">
                  <div className="mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                  <p className="text-gray-400">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Footer */}
          <motion.div
            className="text-center text-gray-500 text-sm"
            variants={itemVariants}
          >
            <p>© 2026 TodoSphere. Crafted with precision.</p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}