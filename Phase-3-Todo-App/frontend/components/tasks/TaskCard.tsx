import { motion } from 'framer-motion';
import { Trash2, Edit3, Calendar, Flag, Clock, Circle, CheckCircle2 } from 'lucide-react';
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
    displayId?: number;  // Simple numeric ID for display
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
  // Local optimistic state for instant feedback
  const [isCompleting, setIsCompleting] = useState(task.completed);
  const [isLoading, setIsLoading] = useState(false);

  // ✅ DEBUG LOG - Check displayId
  console.log('[TaskCard] Rendering:', {
    title: task.title,
    displayId: task.displayId,
    type: typeof task.displayId,
    hasDisplayId: task.displayId !== undefined
  });

  // Update local state when task prop changes
  useEffect(() => {
    setIsCompleting(task.completed);
  }, [task.completed]);

  const handleToggle = async () => {
    if (isLoading) return;

    const newCompleted = !isCompleting;

    // Optimistic update – local UI change
    setIsCompleting(newCompleted);
    setIsLoading(true);

    try {
      // Call parent handler (which does API and state sync)
      await onToggle(task.id, newCompleted);

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

  const getPriorityColor = (priority: 'low' | 'medium' | 'high' | null | undefined) => {
    switch (priority) {
      case 'high':
        return 'text-red-500 bg-red-500/10';
      case 'medium':
        return 'text-yellow-500 bg-yellow-500/10';
      case 'low':
        return 'text-green-500 bg-green-500/10';
      default:
        return 'text-gray-500 bg-gray-500/10';
    }
  };

  const getPriorityBorderColor = (priority: 'low' | 'medium' | 'high' | null | undefined) => {
    switch (priority) {
      case 'high':
        return 'border-l-red-500';
      case 'medium':
        return 'border-l-yellow-500';
      case 'low':
        return 'border-l-green-500';
      default:
        return 'border-l-indigo-500';
    }
  };

  return (
    <motion.div
      custom={index}
      variants={taskCardVariants}
      initial="hidden"
      animate="visible"
      whileHover={{ y: -2, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' }}
      className={cn(
        'relative rounded-xl border bg-card p-4 shadow-sm transition-all duration-200 hover:shadow-md',
        getPriorityBorderColor(task.priority),
        'border-l-4',
        isCompleting ? 'opacity-70 bg-muted/50' : 'bg-card',
        viewMode === 'list' ? 'flex items-start gap-4' : ''
      )}
    >
      {/* Priority indicator bar */}
      <div className={cn(
        'absolute top-0 left-0 h-full w-1 rounded-l-md',
        task.priority === 'high' ? 'bg-red-500' :
        task.priority === 'medium' ? 'bg-yellow-500' :
        task.priority === 'low' ? 'bg-green-500' :
        'bg-indigo-500'
      )} />

      <div className="flex items-start gap-3 flex-1 pl-2">
        <button
          onClick={handleToggle}
          disabled={isLoading}
          className="mt-0.5 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded-full transition-colors"
          aria-label={isCompleting ? "Mark as incomplete" : "Mark as complete"}
        >
          {isCompleting ? (
            <CheckCircle2 className="h-5 w-5 text-green-500" />
          ) : (
            <Circle className="h-5 w-5 text-muted-foreground hover:text-foreground" />
          )}
        </button>

        <div className="flex-1 min-w-0">
          <h3
            className={cn(
              'font-semibold text-base leading-tight mb-1',
              isCompleting ? 'line-through text-muted-foreground' : 'text-foreground'
            )}
          >
            {task.title}
          </h3>

          {task.description && (
            <p className={cn(
              'text-sm text-muted-foreground mb-2',
              isCompleting ? 'line-through' : ''
            )}>
              {task.description}
            </p>
          )}

          <div className="flex flex-wrap items-center gap-3 text-xs">
            {task.dueDate && (
              <div className="flex items-center gap-1 px-2 py-1 bg-secondary rounded-full">
                <Clock className="h-3 w-3 text-muted-foreground" />
                <span className="text-muted-foreground">
                  {new Date(task.dueDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              </div>
            )}

            {task.priority && (
              <div className={cn(
                'flex items-center gap-1 px-2 py-1 rounded-full capitalize font-medium',
                getPriorityColor(task.priority)
              )}>
                <Flag className="h-3 w-3" />
                <span>{task.priority}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1 ml-2">
        {/* Task Number Badge - Right Side */}
        {(typeof task.displayId === 'number' && task.displayId > 0) && (
          <div className="flex-shrink-0">
            <div className="flex items-center justify-center w-7 h-7 rounded-full bg-primary/10 text-primary text-xs font-bold">
              #{task.displayId}
            </div>
          </div>
        )}

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(task.id)}
          className="h-8 w-8 p-0 rounded-lg transition-colors hover:bg-accent"
          aria-label="Edit task"
        >
          <Edit3 className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(task.id)}
          className="h-8 w-8 p-0 text-destructive rounded-lg transition-colors hover:bg-destructive/10 hover:text-destructive"
          aria-label="Delete task"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </motion.div>
  );
}


