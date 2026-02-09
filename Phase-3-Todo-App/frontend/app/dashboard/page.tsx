

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, Grid3X3, List, Calendar, Flag } from 'lucide-react';
import { TaskList } from '@/components/tasks/TaskList';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/shared/EmptyState';
import { SkeletonLoader } from '@/components/shared/SkeletonLoader';
import { fadeInUp } from '@/lib/animations';
import { apiClient, type Task } from '@/lib/api';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { toast } from 'sonner';

export default function DashboardPage() {
  const router = useRouter();
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getTasks('all');
        const fetchedTasks = response?.tasks || response || [];
        setTasks(fetchedTasks);
        console.log('[Dashboard] Tasks after fetch:', tasks.map(t => ({ id: t.id, dueDate: t.dueDate, priority: t.priority })));

        // Add default tasks if no tasks exist
        if (fetchedTasks.length === 0) {
          const defaultTasks = [
            {
              title: "Complete project proposal",
              description: "Finish the proposal document and send to the team.",
              priority: "high" as const,
              dueDate: "2023-11-20",
              completed: false
            },
            {
              title: "Weekly team meeting",
              description: "Weekly team sync to discuss progress",
              priority: "medium" as const,
              dueDate: "2023-11-14",
              completed: false
            },
            {
              title: "Buy groceries",
              description: "Milk, eggs, bread, fruits",
              priority: "low" as const,
              dueDate: "",
              completed: false
            }
          ];

          for (const taskData of defaultTasks) {
            try {
              const response = await apiClient.createTask(taskData);
              setTasks(prev => [response.task, ...prev]);
            } catch (error) {
              console.error('Failed to create default task:', error);
            }
          }

          toast.success("Default tasks added successfully!");
          const updatedResponse = await apiClient.getTasks('all');
          setTasks(updatedResponse?.tasks || updatedResponse || []);
        }
      } catch (err: any) {
        console.error('Failed to fetch tasks:', err);
        setError(err.message || 'Failed to load tasks. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  const filteredTasks = (tasks || []).filter(task =>
    task?.title?.toLowerCase()?.includes(searchTerm.toLowerCase()) ||
    (task?.description && task.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleEdit = (taskId: string) => {
    router.push(`/tasks/${taskId}`);
  };

  const handleCreateTask = async (taskData: any) => {
    try {
      const response = await apiClient.createTask(taskData);
      setTasks([response.task, ...tasks]);
      toast.success('Task created successfully!');
      setShowTaskForm(false);
    } catch (error: any) {
      console.error('Failed to create task:', error);
      toast.error('Failed to create task');
    }
  };

  const handleUpdate = async (updatedTask: Task) => {
    try {
      const response = await apiClient.updateTask(updatedTask.id, updatedTask);
      setTasks(tasks.map(task => task.id === updatedTask.id ? response.task : task));
    } catch (error: any) {
      console.error('Failed to update task:', error);
      toast.error('Failed to update task');
    }
  };

  const handleToggleCompletion = async (taskId: string) => {
    const currentTask = tasks.find(t => t.id === taskId);
    if (!currentTask) return;

    const newCompleted = !currentTask.completed;

    // 1. Optimistic update – UI turant change
    setTasks(prevTasks => prevTasks.map(t =>
      t.id === taskId ? { ...t, completed: newCompleted } : t
    ));

    console.log(`[Toggle] Optimistic UI update for ${taskId} → ${newCompleted ? 'completed' : 'pending'}`);

    try {
      // 2. API call
      await apiClient.toggleTaskCompletion(taskId);
      console.log(`[Toggle] API success for ${taskId}`);

      // 3. Small delay + force page reload (stale data / cache issue fix)
      console.log('[Toggle] Waiting 1s then reloading page for fresh sync');
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay

      // Force reload – ye stale data ka sabse pakka fix hai
      window.location.reload();

      toast.success(`Task marked as ${newCompleted ? 'completed' : 'pending'}`);
    } catch (error: any) {
      console.error(`[Toggle] Failed for ${taskId}:`, error);

      // Rollback UI
      setTasks(prevTasks => prevTasks.map(t =>
        t.id === taskId ? { ...t, completed: currentTask.completed } : t
      ));

      toast.error('Failed to update task status. Please try again.');

      if (error.message?.includes('Unauthorized') || error.message?.includes('401')) {
        toast.error('Session expired, please login again');
        router.push('/auth/signin');
      }
    }
  };

  const handleDelete = async (taskId: string) => {
    try {
      await apiClient.deleteTask(taskId);
      setTasks(tasks.filter(task => task.id !== taskId));
      toast.success('Task deleted successfully!');
    } catch (error: any) {
      console.error('Failed to delete task:', error);
      toast.error('Failed to delete task');
    }
  };

  if (error) {
    return (
      <ProtectedRoute>
        <div className="container mx-auto py-6">
          <div className="text-center py-12">
            <p className="text-destructive">Failed to load tasks: {error}</p>
            <Button className="mt-4" onClick={() => window.location.reload()}>
              Retry
            </Button>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

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
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <h1 className="text-3xl font-bold text-white">My Tasks</h1>

              <div className="flex items-center gap-2 w-full sm:w-auto">
                <div className="relative flex-1 sm:flex-none">
                  <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <input
                    type="text"
                    placeholder="Search tasks..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8 pr-4 py-2 w-full rounded-md border bg-black/30 backdrop-blur-lg text-white placeholder:text-gray-400 border-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-200 hover:shadow-indigo-500/20"
                  />
                </div>

                <Button
                  variant="outline"
                  size="icon"
                  className="border-white/10 bg-black/30 backdrop-blur-lg text-white hover:bg-white/10 hover:text-indigo-400 rounded-lg transition hover:shadow-indigo-500/30"
                  onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                  aria-label="Toggle view mode"
                >
                  {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid3X3 className="h-4 w-4" />}
                </Button>

                <Button
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-indigo-500/30 hover:scale-105 transition-all duration-200"
                  onClick={() => router.push('/tasks/new')}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  New Task
                </Button>
              </div>
            </div>

            {loading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, index) => (
                  <SkeletonLoader key={index} className="h-20 w-full rounded-lg" />
                ))}
              </div>
            ) : filteredTasks.length === 0 ? (
              <EmptyState
                title="No tasks yet"
                description="Get started by creating your first task"
                actionText="Create Task"
                onAction={() => router.push('/tasks/new')}
              />
            ) : (
              <AnimatePresence>
                <TaskList
                  tasks={filteredTasks}
                  viewMode={viewMode}
                  onUpdate={handleUpdate}
                  onToggleCompletion={handleToggleCompletion}
                  onDelete={handleDelete}
                  onEdit={handleEdit}
                />
              </AnimatePresence>
            )}
          </motion.div>
        </div>
      </div>
    </ProtectedRoute>
  );
}