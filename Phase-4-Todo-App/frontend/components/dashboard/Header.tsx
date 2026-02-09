'use client';

import { Menu, Bell, User, Home, LogOut } from 'lucide-react';
import { ThemeToggle } from '@/components/shared/ThemeToggle';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { usePathname } from 'next/navigation';
import { toast } from 'sonner';

interface HeaderProps {
  onMenuClick: () => void;
  sidebarOpen: boolean;
}

export function Header({ onMenuClick, sidebarOpen }: HeaderProps) {
  const { logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleTopRightAction = () => {
    // If on dashboard page, always redirect to login
    if (pathname === '/dashboard') {
      router.push('/auth/signin');
    } else if (isAuthenticated()) {
      // If authenticated and not on dashboard, redirect to dashboard
      router.push('/dashboard');
    } else {
      // If not authenticated, redirect to login
      router.push('/auth/signin');
    }
  };

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    router.push('/auth/signin');
  };

  return (
    <motion.header
      className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50"
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
    >
      <div className="flex h-16 items-center px-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="mr-2 md:hidden"
          aria-label="Toggle sidebar"
        >
          <Menu className={`h-5 w-5 ${sidebarOpen ? 'rotate-180' : ''}`} />
        </Button>

        <div className="flex-1">
          <h1 className="text-xl font-bold">Beautiful Todo</h1>
        </div>

        <div className="flex items-center gap-1 sm:gap-2">
          <Button variant="ghost" size="icon" aria-label="Notifications" className="h-9 w-9">
            <Bell className="h-4 w-4" />
          </Button>

          <ThemeToggle />

          {/* Top-right action button - acts as home/dashboard button, redirects based on auth status */}
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 rounded-full"
            aria-label={isAuthenticated() ? "Go to Dashboard" : "Go to Login"}
            onClick={handleTopRightAction}
          >
            <Home className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </motion.header>
  );
}