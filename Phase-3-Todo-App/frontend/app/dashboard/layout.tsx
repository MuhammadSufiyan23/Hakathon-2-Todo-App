'use client';

import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';
import { Header } from '@/components/dashboard/Header';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { useMobile } from '@/hooks/use-mobile';
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';

function DashboardContent({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();

  return (
    <>
      <main className="flex-1 overflow-y-auto p-4 pb-20 md:p-6 md:pb-6">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          className="container mx-auto"
        >
          {children}
        </motion.div>
      </main>
    </>
  );
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const isMobile = useMobile();
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar for desktop */}
      {!isMobile && (
        <aside className="hidden md:block w-64 bg-background border-r">
          <Sidebar />
        </aside>
      )}

      {/* Mobile sidebar - conditionally rendered */}
      {isMobile && sidebarOpen && (
        <motion.aside
          className="fixed inset-y-0 left-0 z-50 w-64 bg-background border-r md:hidden"
          initial={{ x: '-100%' }}
          animate={{ x: 0 }}
          exit={{ x: '-100%' }}
          transition={{ type: "spring", damping: 25, stiffness: 200 }}
        >
          <Sidebar />
        </motion.aside>
      )}

      {/* Overlay for mobile sidebar */}
      {isMobile && sidebarOpen && (
        <motion.div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 md:hidden"
          onClick={() => setSidebarOpen(false)}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.5 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        />
      )}

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />

        <DashboardContent>{children}</DashboardContent>
      </div>
    </div>
  );
}