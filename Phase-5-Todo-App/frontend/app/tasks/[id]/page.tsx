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
import { ArrowLeft, Calendar, Flag, Trash2, Save } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function EditTaskPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const taskId = params.id;

  const [task, setTask] = useState<Task | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [completed, setCompleted] = useState(false);
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
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
        setDueDate(response.dueDate || '');
        setPriority(response.priority || 'medium');
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

    setSaving(true);
    try {
      await apiClient.updateTask(taskId, {
        title: title.trim(),
        description: description.trim(),
        completed,
        dueDate: dueDate || null,
        priority,
      });

      toast.success('Task updated successfully!');
      router.push('/dashboard');
      router.refresh();
    } catch (error) {
      console.error('Failed to update task:', error);
      toast.error('Failed to update task');
    } finally {
      setSaving(false);
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
      router.refresh();
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
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950/50 to-purple-950/50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center"
          >
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto"></div>
            <p className="mt-4 text-gray-400">Loading task...</p>
          </motion.div>
        </div>
      </ProtectedRoute>
    );
  }

  if (!task) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950/50 to-purple-950/50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <h2 className="text-2xl font-bold text-red-400">Task not found</h2>
            <p className="mt-2 text-gray-400">The requested task could not be found.</p>
            <Button
              className="mt-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
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
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950/50 to-purple-950/50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-2xl"
        >
          <Card className="bg-black/30 backdrop-blur-xl border-white/10 shadow-2xl rounded-2xl">
            <CardHeader className="border-b border-white/10">
              <CardTitle className="text-2xl font-bold bg-gradient-to-r from-white via-indigo-200 to-purple-200 bg-clip-text text-transparent">
                Edit Task
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleUpdate} className="space-y-6">
                {/* Title */}
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-white mb-2">
                    Title *
                  </label>
                  <div className="relative">
                    <Flag className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="title"
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      placeholder="Enter task title"
                      required
                      className="bg-black/30 backdrop-blur-lg text-white placeholder:text-gray-400 border-white/10 focus:ring-2 focus:ring-indigo-500 pl-10 rounded-xl"
                    />
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-white mb-2">
                    Description
                  </label>
                  <Textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Enter task description"
                    rows={4}
                    className="bg-black/30 backdrop-blur-lg text-white placeholder:text-gray-400 border-white/10 focus:ring-2 focus:ring-indigo-500 rounded-xl"
                  />
                </div>

                {/* Due Date and Priority Row */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Due Date */}
                  <div>
                    <label htmlFor="dueDate" className="block text-sm font-medium text-white mb-2">
                      Due Date
                    </label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                      <Input
                        id="dueDate"
                        type="date"
                        value={dueDate}
                        onChange={(e) => setDueDate(e.target.value)}
                        className="bg-black/30 backdrop-blur-lg text-white border-white/10 focus:ring-2 focus:ring-indigo-500 pl-10 rounded-xl"
                      />
                    </div>
                  </div>

                  {/* Priority */}
                  <div>
                    <label htmlFor="priority" className="block text-sm font-medium text-white mb-2">
                      Priority
                    </label>
                    <Select value={priority} onValueChange={(value) => setPriority(value as 'low' | 'medium' | 'high')}>
                      <SelectTrigger className="bg-black/30 backdrop-blur-lg border-white/10 text-white rounded-xl focus:ring-2 focus:ring-indigo-500">
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-900 border-white/10">
                        <SelectItem value="low">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500" />
                            Low
                          </div>
                        </SelectItem>
                        <SelectItem value="medium">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-yellow-500" />
                            Medium
                          </div>
                        </SelectItem>
                        <SelectItem value="high">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-red-500" />
                            High
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Completed Checkbox */}
                <div className="flex items-center space-x-3 p-4 bg-white/5 rounded-xl border border-white/10">
                  <input
                    type="checkbox"
                    id="completed"
                    checked={completed}
                    onChange={() => toggleComplete()}
                    className="h-5 w-5 rounded border-white/20 bg-black/30 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-0"
                  />
                  <label htmlFor="completed" className="text-sm font-medium text-white cursor-pointer">
                    Mark as completed
                  </label>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col sm:flex-row justify-between gap-3 pt-4">
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => router.push('/dashboard')}
                      className="border-white/10 bg-black/30 backdrop-blur-lg text-white hover:bg-white/10 rounded-xl"
                    >
                      <ArrowLeft className="mr-2 h-4 w-4" />
                      Back
                    </Button>
                    <Button
                      type="button"
                      variant="destructive"
                      onClick={handleDelete}
                      disabled={deleting}
                      className="bg-red-600 hover:bg-red-700 rounded-xl"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      {deleting ? 'Deleting...' : 'Delete'}
                    </Button>
                  </div>

                  <Button
                    type="submit"
                    disabled={saving}
                    className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-indigo-500/50 hover:scale-105 transition-all rounded-xl"
                  >
                    <Save className="mr-2 h-4 w-4" />
                    {saving ? 'Saving...' : 'Save Changes'}
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