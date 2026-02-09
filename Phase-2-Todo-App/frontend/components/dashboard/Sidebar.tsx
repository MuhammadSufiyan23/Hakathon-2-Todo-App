'use client';

import Link from 'next/link';
import { Home, Plus, Filter, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { slideInFromLeft } from '@/lib/animations';

export function Sidebar() {
  return (
    <motion.div
      className="flex h-full flex-col px-4 py-6"
      initial="hidden"
      animate="visible"
      variants={slideInFromLeft}
    >
      <div className="mb-8">
        <h2 className="text-xl font-bold">Todo Dashboard</h2>
      </div>

      <nav className="flex flex-1 flex-col gap-2">
        <Button
          variant="ghost"
          className="justify-start"
          asChild
        >
          <Link href="/dashboard">
            <Home className="mr-2 h-4 w-4" />
            Dashboard
          </Link>
        </Button>

        <Button
          variant="ghost"
          className="justify-start"
          asChild
        >
          <Link href="/tasks/new">
            <Plus className="mr-2 h-4 w-4" />
            New Task
          </Link>
        </Button>

        <Button
          variant="ghost"
          className="justify-start"
          asChild
        >
          <Link href="/tasks/all">
            <Filter className="mr-2 h-4 w-4" />
            All Tasks
          </Link>
        </Button>

        <Button
          variant="ghost"
          className="justify-start"
          asChild
        >
          <Link href="/tasks/pending">
            <Calendar className="mr-2 h-4 w-4" />
            Pending
          </Link>
        </Button>

        <Button
          variant="ghost"
          className="justify-start"
          asChild
        >
          <Link href="/tasks/completed">
            <Calendar className="mr-2 h-4 w-4" />
            Completed
          </Link>
        </Button>
      </nav>
    </motion.div>
  );
}