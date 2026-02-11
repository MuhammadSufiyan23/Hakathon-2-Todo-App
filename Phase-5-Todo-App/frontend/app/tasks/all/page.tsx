'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { TaskList } from '@/components/tasks/TaskList';
import { SkeletonLoader } from '@/components/shared/SkeletonLoader';
import { EmptyState } from '@/components/shared/EmptyState';
import { apiClient, type Task } from '@/lib/api';
import { fadeInUp } from '@/lib/animations';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { toast } from 'sonner';
import { ArrowLeft, LogOut, Home } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';

export default function AllTasksPage() {
  const router = useRouter();
  const { logout, isAuthenticated } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleTopRightAction = () => {
    if (isAuthenticated()) {
      // If authenticated, redirect to dashboard
      router.push('/dashboard');
    } else {
      // If not authenticated, redirect to login
      router.push('/auth/signin');
    }
  };

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getTasks('all');
        // Safe fallback: if response.tasks doesn't exist, use an empty array
        setTasks(response?.tasks || response || []);
      } catch (err: any) {
        console.error('Failed to fetch tasks:', err);
        setError(err.message || 'Failed to load tasks. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const handleUpdate = (updatedTask: Task) => {
    setTasks(tasks.map(task => task.id === updatedTask.id ? updatedTask : task));
  };

  const handleToggleCompletion = async (taskId: string) => {
    // Find the task to get its current state
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    const newCompleted = !task.completed;

    // Optimistic update - immediately update UI
    setTasks(tasks.map(t =>
      t.id === taskId ? { ...t, completed: newCompleted } : t
    ));

    try {
      // Make the API call to toggle completion
      const response = await apiClient.toggleTaskCompletion(taskId);

      // Update the task in the state with the response
      setTasks(tasks.map(t =>
        t.id === taskId ? response.task : t
      ));

      toast.success(`Task marked as ${newCompleted ? 'completed' : 'pending'}`);
    } catch (error: any) {
      // Rollback on error - revert the optimistic update
      setTasks(tasks.map(t =>
        t.id === taskId ? { ...t, completed: task.completed } : t
      ));

      console.error('Failed to toggle task completion:', error);
      toast.error('Failed to update task status, please try again');

      // Check if it's a token/session issue
      if (error.message.includes('Unauthorized') || error.message.includes('401')) {
        toast.error('Session expired, please login again');
        router.push('/auth/signin');
      }
      // Don't re-throw error to prevent page crashes - error handling is complete
    }
  };

  const handleDelete = (deletedTaskId: string) => {
    setTasks(tasks.filter(task => task.id !== deletedTaskId));
  };

  const handleEdit = (taskId: string) => {
    router.push(`/tasks/${taskId}`);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950/50 to-purple-950/50">
        <div className="container mx-auto py-6">
          <motion.div
            className="space-y-6"
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
          >
            <div className="relative">
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full absolute top-6 right-6 z-20"
                onClick={handleTopRightAction}
                aria-label={isAuthenticated() ? "Go to Dashboard" : "Go to Login"}
              >
                <Home className="h-5 w-5" />
              </Button>

              <h1 className="text-3xl font-bold text-white">All Tasks</h1>
            </div>

            {loading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, index) => (
                  <SkeletonLoader
                    key={index}
                    className="h-20 w-full rounded-lg"
                  />
                ))}
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <p className="text-destructive">{error}</p>
              </div>
            ) : !tasks || tasks.length === 0 ? (
              <EmptyState
                title="No tasks found"
                description="There are no tasks in your list"
                actionText="Create Task"
                onAction={() => router.push('/tasks/new')}
              />
            ) : (
              <TaskList
                tasks={tasks}
                viewMode="grid"
                onUpdate={handleUpdate}
                onToggleCompletion={handleToggleCompletion}
                onDelete={handleDelete}
                onEdit={handleEdit}
              />
            )}
          </motion.div>
        </div>
      </div>
    </ProtectedRoute>
  );
}