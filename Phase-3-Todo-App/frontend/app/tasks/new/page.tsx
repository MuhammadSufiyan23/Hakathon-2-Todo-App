'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ArrowLeft, LogOut, Home } from 'lucide-react';
import { Calendar, Flag } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

export default function NewTaskPage() {
  const router = useRouter();
  const { logout, isAuthenticated } = useAuth();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [loading, setLoading] = useState(false);

  const handleTopRightAction = () => {
    if (isAuthenticated()) {
      // If authenticated, redirect to dashboard
      router.push('/dashboard');
    } else {
      // If not authenticated, redirect to login
      router.push('/auth/signin');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      toast.error('Title is required');
      return;
    }

    setLoading(true);
    try {
      const taskData = {
        title: title.trim(),
        description: description.trim() || undefined,
        completed: false,
        dueDate: dueDate || null,
        priority: priority,
      };

      console.log('[New Task Form] Sending to backend:', taskData); // Ye log check karne ke liye

      await apiClient.createTask(taskData);

      toast.success('Task created successfully!');
      router.push('/dashboard');
      router.refresh();
    } catch (error) {
      console.error('Failed to create task:', error);
      toast.error('Failed to create task');
    } finally {
      setLoading(false);
    }
  };


  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-indigo-950/50 to-purple-950/50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-lg"
        >
          <Card className="bg-black/30 backdrop-blur-lg border-white/10 shadow-xl rounded-2xl">
            <CardHeader className="relative">
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full absolute top-6 right-6 z-20"
                onClick={handleTopRightAction}
                aria-label={isAuthenticated() ? "Go to Dashboard" : "Go to Login"}
              >
                <Home className="h-5 w-5" />
              </Button>

              <CardTitle className="text-2xl font-bold text-white">Create New Task</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-white mb-1">
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
                      className="bg-black/30 backdrop-blur-lg text-white placeholder:text-gray-400 border-white/10 focus:outline-none focus:ring-1 focus:ring-indigo-500 pl-10"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-white mb-1">
                    Description
                  </label>
                  <Textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Enter task description"
                    rows={4}
                    className="bg-black/30 backdrop-blur-lg text-white placeholder:text-gray-400 border-white/10 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label htmlFor="dueDate" className="block text-sm font-medium text-white mb-1">
                    Due Date
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="dueDate"
                      type="date"
                      value={dueDate}
                      onChange={(e) => setDueDate(e.target.value)}
                      className="bg-black/30 backdrop-blur-lg text-white placeholder:text-gray-400 border-white/10 focus:outline-none focus:ring-1 focus:ring-indigo-500 pl-10"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="priority" className="block text-sm font-medium text-white mb-1">
                    Priority
                  </label>
                  <select
                    id="priority"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
                    className="w-full rounded-md border border-white/10 bg-black/30 backdrop-blur-lg text-white px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="low" className="bg-gray-800">Low</option>
                    <option value="medium" className="bg-gray-800">Medium</option>
                    <option value="high" className="bg-gray-800">High</option>
                  </select>
                </div>

                <div className="flex justify-end pt-2">
                  <Button
                    type="submit"
                    disabled={loading}
                    className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 shadow-lg hover:shadow-xl hover:scale-105 transition-all"
                  >
                    {loading ? 'Creating...' : 'Create Task'}
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