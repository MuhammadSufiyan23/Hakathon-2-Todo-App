

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, Grid3X3, List, Calendar, Flag, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { TaskList } from '@/components/tasks/TaskList';
import { Button } from '@/components/ui/button';
import { EmptyState } from '@/components/shared/EmptyState';
import { SkeletonLoader } from '@/components/shared/SkeletonLoader';
import { fadeInUp } from '@/lib/animations';
import { apiClient, type Task } from '@/lib/api';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { toast } from 'sonner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function DashboardPage() {
  const router = useRouter();
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
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

  // Calculate statistics
  const stats = {
    total: tasks.length,
    completed: tasks.filter(t => t.completed).length,
    pending: tasks.filter(t => !t.completed).length,
    high: tasks.filter(t => t.priority === 'high').length,
    medium: tasks.filter(t => t.priority === 'medium').length,
    low: tasks.filter(t => t.priority === 'low').length,
  };

  const filteredTasks = (tasks || []).filter(task => {
    const matchesSearch = task?.title?.toLowerCase()?.includes(searchTerm.toLowerCase()) ||
      (task?.description && task.description.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesPriority = priorityFilter === 'all' || task?.priority === priorityFilter;

    return matchesSearch && matchesPriority;
  });

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
        <div className="container mx-auto py-8 px-4">
          <motion.div
            className="space-y-8"
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
          >
            {/* Header */}
            <div className="flex flex-col gap-2">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-indigo-200 to-purple-200 bg-clip-text text-transparent">
                My Tasks
              </h1>
              <p className="text-gray-400">Manage your tasks with priorities and filters</p>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {/* Total Tasks */}
              <motion.div
                whileHover={{ scale: 1.05, y: -4 }}
                className="bg-gradient-to-br from-indigo-500/20 to-purple-500/20 backdrop-blur-xl border border-indigo-500/30 rounded-2xl p-4 shadow-lg hover:shadow-indigo-500/30 transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-500/20 rounded-lg">
                    <Calendar className="h-5 w-5 text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.total}</p>
                    <p className="text-xs text-gray-400">Total</p>
                  </div>
                </div>
              </motion.div>

              {/* Completed */}
              <motion.div
                whileHover={{ scale: 1.05, y: -4 }}
                className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-xl border border-green-500/30 rounded-2xl p-4 shadow-lg hover:shadow-green-500/30 transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-500/20 rounded-lg">
                    <CheckCircle2 className="h-5 w-5 text-green-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.completed}</p>
                    <p className="text-xs text-gray-400">Completed</p>
                  </div>
                </div>
              </motion.div>

              {/* Pending */}
              <motion.div
                whileHover={{ scale: 1.05, y: -4 }}
                className="bg-gradient-to-br from-yellow-500/20 to-orange-500/20 backdrop-blur-xl border border-yellow-500/30 rounded-2xl p-4 shadow-lg hover:shadow-yellow-500/30 transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-yellow-500/20 rounded-lg">
                    <Clock className="h-5 w-5 text-yellow-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.pending}</p>
                    <p className="text-xs text-gray-400">Pending</p>
                  </div>
                </div>
              </motion.div>

              {/* High Priority */}
              <motion.div
                whileHover={{ scale: 1.05, y: -4 }}
                className="bg-gradient-to-br from-red-500/20 to-pink-500/20 backdrop-blur-xl border border-red-500/30 rounded-2xl p-4 shadow-lg hover:shadow-red-500/30 transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-red-500/20 rounded-lg">
                    <AlertCircle className="h-5 w-5 text-red-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.high}</p>
                    <p className="text-xs text-gray-400">High</p>
                  </div>
                </div>
              </motion.div>

              {/* Medium Priority */}
              <motion.div
                whileHover={{ scale: 1.05, y: -4 }}
                className="bg-gradient-to-br from-yellow-500/20 to-amber-500/20 backdrop-blur-xl border border-yellow-500/30 rounded-2xl p-4 shadow-lg hover:shadow-yellow-500/30 transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-yellow-500/20 rounded-lg">
                    <Flag className="h-5 w-5 text-yellow-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.medium}</p>
                    <p className="text-xs text-gray-400">Medium</p>
                  </div>
                </div>
              </motion.div>

              {/* Low Priority */}
              <motion.div
                whileHover={{ scale: 1.05, y: -4 }}
                className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-xl border border-blue-500/30 rounded-2xl p-4 shadow-lg hover:shadow-blue-500/30 transition-all duration-200"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <Flag className="h-5 w-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{stats.low}</p>
                    <p className="text-xs text-gray-400">Low</p>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Toolbar */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 bg-black/20 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 w-full lg:w-auto">
                {/* Search */}
                <div className="relative flex-1 sm:flex-none w-full sm:w-64">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <input
                    type="text"
                    placeholder="Search tasks..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-2.5 w-full rounded-xl border bg-black/30 backdrop-blur-lg text-white placeholder:text-gray-400 border-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
                  />
                </div>

                {/* Priority Filter */}
                <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                  <SelectTrigger className="w-full sm:w-40 bg-black/30 backdrop-blur-lg border-white/10 text-white rounded-xl">
                    <SelectValue placeholder="Priority" />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-900 border-white/10">
                    <SelectItem value="all">All Priorities</SelectItem>
                    <SelectItem value="high">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-red-500" />
                        High
                      </div>
                    </SelectItem>
                    <SelectItem value="medium">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-yellow-500" />
                        Medium
                      </div>
                    </SelectItem>
                    <SelectItem value="low">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500" />
                        Low
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center gap-2 w-full lg:w-auto">
                {/* View Mode Toggle */}
                <Button
                  variant="outline"
                  size="icon"
                  className="border-white/10 bg-black/30 backdrop-blur-lg text-white hover:bg-white/10 hover:text-indigo-400 rounded-xl transition hover:shadow-indigo-500/30"
                  onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                  aria-label="Toggle view mode"
                >
                  {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid3X3 className="h-4 w-4" />}
                </Button>

                {/* New Task Button */}
                <Button
                  className="flex-1 lg:flex-none bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-indigo-500/50 hover:scale-105 transition-all duration-200 rounded-xl"
                  onClick={() => router.push('/tasks/new')}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  New Task
                </Button>
              </div>
            </div>

            {/* Tasks List */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, index) => (
                  <SkeletonLoader key={index} className="h-[180px] w-full rounded-2xl bg-white/5" />
                ))}
              </div>
            ) : filteredTasks.length === 0 ? (
              <EmptyState
                title={searchTerm || priorityFilter !== 'all' ? "No tasks found" : "No tasks yet"}
                description={searchTerm || priorityFilter !== 'all' ? "Try adjusting your filters" : "Get started by creating your first task"}
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