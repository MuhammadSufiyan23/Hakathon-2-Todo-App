'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { apiClient, type Task } from '@/lib/api';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ArrowLeft } from 'lucide-react';

export default function EditTaskPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const taskId = params.id;

  const [task, setTask] = useState<Task | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [completed, setCompleted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  // Fetch task data
  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await apiClient.getTaskById(taskId);
        setTask(response);
        setTitle(response.title);
        setDescription(response.description || '');
        setCompleted(response.completed);
      } catch (error) {
        console.error('Failed to fetch task:', error);
        toast.error('Failed to load task');
        router.push('/dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchTask();
  }, [taskId, router]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      toast.error('Title is required');
      return;
    }

    try {
      await apiClient.updateTask(taskId, {
        title: title.trim(),
        description: description.trim(),
        completed,
      });

      toast.success('Task updated successfully!');
      router.push('/dashboard');
      router.refresh(); // Refresh to show updated task
    } catch (error) {
      console.error('Failed to update task:', error);
      toast.error('Failed to update task');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setDeleting(true);
    try {
      await apiClient.deleteTask(taskId);

      toast.success('Task deleted successfully!');
      router.push('/dashboard');
      router.refresh(); // Refresh to remove task from list
    } catch (error) {
      console.error('Failed to delete task:', error);
      toast.error('Failed to delete task');
      setDeleting(false);
    }
  };

  const toggleComplete = async () => {
    try {
      await apiClient.updateTask(taskId, {
        completed: !completed,
      });

      setCompleted(!completed);
      toast.success(completed ? 'Task marked as pending' : 'Task marked as completed');
    } catch (error) {
      console.error('Failed to update task completion:', error);
      toast.error('Failed to update task status');
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading task...</p>
          </motion.div>
        </div>
      </ProtectedRoute>
    );
  }

  if (!task) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <h2 className="text-2xl font-bold text-destructive">Task not found</h2>
            <p className="mt-2 text-muted-foreground">The requested task could not be found.</p>
            <Button
              className="mt-4"
              onClick={() => router.push('/dashboard')}
            >
              Go to Dashboard
            </Button>
          </motion.div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <Card>
            <CardHeader>
              <CardTitle>Edit Task</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdate} className="space-y-4">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium mb-1">
                    Title *
                  </label>
                  <Input
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Enter task title"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-medium mb-1">
                    Description
                  </label>
                  <Textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Enter task description"
                    rows={4}
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="completed"
                    checked={completed}
                    onChange={() => toggleComplete()}
                    className="h-4 w-4 rounded border-input text-indigo-600 focus:ring-indigo-500"
                  />
                  <label htmlFor="completed" className="text-sm font-medium">
                    Mark as completed
                  </label>
                </div>

                <div className="flex justify-between pt-2">
                  <div className="flex space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => router.push('/dashboard')}
                    >
                      <ArrowLeft className="mr-2 h-4 w-4" />
                      Back to Dashboard
                    </Button>
                    <Button
                      type="button"
                      variant="destructive"
                      onClick={handleDelete}
                      disabled={deleting}
                    >
                      {deleting ? 'Deleting...' : 'Delete'}
                    </Button>
                  </div>

                  <Button type="submit">
                    Update Task
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </ProtectedRoute>
  );
}