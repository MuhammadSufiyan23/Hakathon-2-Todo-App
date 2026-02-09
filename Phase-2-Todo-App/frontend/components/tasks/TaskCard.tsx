import { motion } from 'framer-motion';
import { Trash2, Edit3, Calendar, Flag } from 'lucide-react';
import { TaskCompletionAnimation } from '@/components/tasks/TaskCompletionAnimation';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { taskCardVariants } from '@/lib/animations';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';

interface TaskCardProps {
  task: {
    id: string;
    title: string;
    description?: string;
    completed: boolean;
    dueDate: string | null;
    priority: 'low' | 'medium' | 'high' | null;
  };
  index?: number;
  onToggle: (id: string, newCompleted: boolean) => Promise<void>; // Parent ko await karne ke liye
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  viewMode?: 'grid' | 'list';
}

export function TaskCard({
  task,
  index = 0,
  onToggle,
  onEdit,
  onDelete,
  viewMode = 'grid'
}: TaskCardProps) {
  // Debug log as requested
  console.log('[TaskCard] Received task for render:', { dueDate: task?.dueDate, priority: task?.priority });

  // Local optimistic state for instant feedback
  const [isCompleting, setIsCompleting] = useState(task.completed);
  const [isLoading, setIsLoading] = useState(false);

  // Debug logging to confirm data is received
  useEffect(() => {
    console.log(`[TaskCard] Task data for ${task.id}:`, {
      title: task.title,
      dueDate: task.dueDate,
      priority: task.priority,
      completed: task.completed
    });
    setIsCompleting(task.completed);
  }, [task]);

  const handleToggle = async () => {
    if (isLoading) return;

    const newCompleted = !isCompleting;

    // Optimistic update – local UI change
    setIsCompleting(newCompleted);
    setIsLoading(true);
    console.log(`[TaskCard] Optimistic update for ${task.id}: completed = ${newCompleted}`);

    try {
      // Call parent handler (which does API and state sync)
      await onToggle(task.id, newCompleted);

      console.log(`[TaskCard] Toggle success for ${task.id}`);
      toast.success(`Task marked as ${newCompleted ? 'completed' : 'pending'}`);
      // No rollback on success
    } catch (err: any) {
      console.error(`[TaskCard] Toggle failed for ${task.id}:`, err);
      // Rollback local state only on error
      setIsCompleting(task.completed);
      toast.error(err.message || 'Failed to update task status');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-500';
      case 'medium':
        return 'text-yellow-500';
      case 'low':
        return 'text-green-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <motion.div
      custom={index}
      variants={taskCardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className={cn(
        'rounded-2xl border border-white/10 bg-gradient-to-br from-indigo-950/20 to-purple-950/20 backdrop-blur-lg shadow-xl p-4',
        'transition-all duration-300 hover:shadow-2xl hover:shadow-indigo-500/30 hover:scale-[1.02]',
        isCompleting ? 'opacity-70' : 'opacity-100',
        viewMode === 'list' ? 'flex items-start' : ''
      )}
    >
      <div className="flex items-start gap-3 flex-1">
        <button
          onClick={handleToggle}
          disabled={isLoading}
          className="mt-1 focus:outline-none"
          aria-label={isCompleting ? "Mark as incomplete" : "Mark as complete"}
        >
          <TaskCompletionAnimation completed={isCompleting} isLoading={isLoading} />
        </button>

        <div className="flex-1 min-w-0">
          <h3
            className={cn(
              'font-bold truncate',
              isCompleting ? 'line-through text-muted-foreground' : 'text-foreground'
            )}
          >
            {task.title}
          </h3>

          {task.description && (
            <p className={cn(
              'text-sm mt-1 text-muted-foreground italic',
              'truncate max-w-xs sm:max-w-md',
              isCompleting ? 'line-through' : ''
            )}>
              {task.description}
            </p>
          )}

          <div className="flex items-center gap-4 mt-2">
            <div className="flex items-center gap-2 text-sm text-gray-300 mt-2">
              <Calendar className="h-4 w-4 text-indigo-400" />
              <span>{task?.dueDate ? new Date(task.dueDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'No due date'}</span>
            </div>

            {task?.priority && (
              <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium mt-2 ${
                task.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-green-500/20 text-green-400'
              }`}>
                <Flag className="h-3 w-3" />
                <span className="capitalize">{task.priority}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1 ml-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(task.id)}
          className="h-8 w-8 p-0 hover:text-indigo-400 hover:bg-white/10 rounded-lg transition hover:shadow-indigo-500/20"
          aria-label="Edit task"
        >
          <Edit3 className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(task.id)}
          className="h-8 w-8 p-0 text-red-500 hover:text-red-400 hover:bg-white/10 rounded-lg transition hover:shadow-red-500/20"
          aria-label="Delete task"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </motion.div>
  );
}


