'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, Grid3X3, List } from 'lucide-react';
import { TaskList } from '@/components/tasks/TaskList';
import { Button } from '@/components/ui/button';
import { TaskForm } from '@/components/tasks/TaskForm';
import { EmptyState } from '@/components/shared/EmptyState';
import { SkeletonLoader } from '@/components/shared/SkeletonLoader';
import { fadeInUp } from '@/lib/animations';
import { apiClient, type Task } from '@/lib/api';
import { useTasks } from '@/hooks/use-tasks';
import { useCreateTask } from '@/hooks/use-tasks';
import { useUpdateTask } from '@/hooks/use-tasks';
import { useDeleteTask } from '@/hooks/use-tasks';
import { toast } from 'sonner';

export function TaskDashboard() {
  const router = useRouter();
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid'); // 'grid' or 'list'
  const [searchTerm, setSearchTerm] = useState('');

  // Using react-query hooks for data fetching and mutations
  const { data, isLoading, isError, error } = useTasks();
  const createTaskMutation = useCreateTask();
  const updateTaskMutation = useUpdateTask();
  const deleteTaskMutation = useDeleteTask();

  // Get tasks from query result
  const allTasks = data?.tasks || [];

  // Filter tasks based on search term
  const filteredTasks = allTasks.filter(task =>
    task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (task.description && task.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleEdit = (taskId: string) => {
    router.push(`/tasks/${taskId}`);
  };

  const handleCreateTask = async (taskData: any) => {
    try {
      await createTaskMutation.mutateAsync(taskData);
      toast.success('Task created successfully!');
      setShowTaskForm(false);
    } catch (error) {
      console.error('Failed to create task:', error);
      toast.error('Failed to create task');
    }
  };

  const handleUpdate = async (updatedTask: Task) => {
    try {
      await updateTaskMutation.mutateAsync({ id: updatedTask.id, data: updatedTask });
    } catch (error) {
      console.error('Failed to update task:', error);
      toast.error('Failed to update task');
    }
  };

  const handleDelete = async (taskId: string) => {
    try {
      await deleteTaskMutation.mutateAsync(taskId);
      toast.success('Task deleted successfully!');
    } catch (error) {
      console.error('Failed to delete task:', error);
      toast.error('Failed to delete task');
    }
  };

  if (isError) {
    return (
      <div className="text-center py-12">
        <p className="text-destructive">Failed to load tasks: {(error as Error)?.message || 'Unknown error'}</p>
        <Button
          className="mt-4"
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </div>
    );
  }

  return (
    <motion.div
      className="space-y-6"
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
    >
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold">My Tasks</h1>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:flex-none">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-4 py-2 w-full rounded-md border bg-background"
            />
          </div>

          <Button
            variant="outline"
            size="icon"
            onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            aria-label="Toggle view mode"
          >
            {viewMode === 'grid' ? <List className="h-4 w-4" /> : <Grid3X3 className="h-4 w-4" />}
          </Button>

          <Button
            onClick={() => router.push('/tasks/new')}
            disabled={createTaskMutation.isPending}
          >
            <Plus className="mr-2 h-4 w-4" />
            New Task
          </Button>
        </div>
      </div>

      {showTaskForm && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
        >
          <TaskForm
            onClose={() => setShowTaskForm(false)}
            onSubmit={handleCreateTask}
          />
        </motion.div>
      )}

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, index) => (
            <SkeletonLoader
              key={index}
              className="h-20 w-full rounded-lg"
            />
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
            onDelete={handleDelete}
            onEdit={handleEdit}
          />
        </AnimatePresence>
      )}
    </motion.div>
  );
}