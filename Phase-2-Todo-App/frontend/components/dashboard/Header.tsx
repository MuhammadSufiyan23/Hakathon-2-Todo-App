'use client';

import { Menu, Bell, User, LogOut } from 'lucide-react';
import { ThemeToggle } from '@/components/shared/ThemeToggle';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface HeaderProps {
  onMenuClick: () => void;
  sidebarOpen: boolean;
}

export function Header({ onMenuClick, sidebarOpen }: HeaderProps) {
  const { logout } = useAuth();
  const router = useRouter();

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

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" aria-label="Notifications">
            <Bell className="h-5 w-5" />
          </Button>

          <ThemeToggle />

          <Button
            variant="ghost"
            size="icon"
            className="rounded-full"
            aria-label="Logout"
            onClick={handleLogout}
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </motion.header>
  );
}