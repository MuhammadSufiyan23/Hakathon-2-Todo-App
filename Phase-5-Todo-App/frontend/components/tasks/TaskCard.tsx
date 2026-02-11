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
      whileHover={{
        y: -4,
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.08)',
        transition: { duration: 0.2 }
      }}
      className={cn(
        'group relative rounded-2xl border-2 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm',
        'p-5 shadow-lg transition-all duration-300 hover:shadow-xl',
        'min-h-[180px] max-h-[180px] overflow-hidden',
        getPriorityBorderColor(task.priority),
        'border-l-[6px]',
        isCompleting ? 'opacity-60 bg-muted/30' : '',
        viewMode === 'list' ? 'flex items-start gap-4' : ''
      )}
    >
      {/* Task ID Badge - Top Right Corner */}
      {(typeof task.displayId === 'number' && task.displayId > 0) && (
        <div className="absolute top-3 right-3 z-10">
          <div className={cn(
            "flex items-center justify-center min-w-[32px] h-8 px-2.5 rounded-full",
            "bg-gradient-to-br from-primary/20 to-primary/10 backdrop-blur-sm",
            "border-2 border-primary/30 shadow-sm",
            "text-primary text-sm font-bold tracking-tight",
            "transition-all duration-200 group-hover:scale-110 group-hover:shadow-md"
          )}>
            #{task.displayId}
          </div>
        </div>
      )}

      {/* Priority Glow Effect */}
      <div className={cn(
        'absolute top-0 left-0 h-full w-1.5 rounded-l-xl opacity-80',
        task.priority === 'high' ? 'bg-gradient-to-b from-red-500 to-red-600 shadow-[0_0_15px_rgba(239,68,68,0.5)]' :
        task.priority === 'medium' ? 'bg-gradient-to-b from-yellow-500 to-yellow-600 shadow-[0_0_15px_rgba(234,179,8,0.5)]' :
        task.priority === 'low' ? 'bg-gradient-to-b from-green-500 to-green-600 shadow-[0_0_15px_rgba(34,197,94,0.5)]' :
        'bg-gradient-to-b from-indigo-500 to-indigo-600 shadow-[0_0_15px_rgba(99,102,241,0.5)]'
      )} />

      <div className="flex items-start gap-4 h-full pl-1">
        <button
          onClick={handleToggle}
          disabled={isLoading}
          className={cn(
            "mt-1 flex-shrink-0 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded-full",
            "transition-all duration-200 hover:scale-110 active:scale-95",
            isLoading && "opacity-50 cursor-not-allowed"
          )}
          aria-label={isCompleting ? "Mark as incomplete" : "Mark as complete"}
        >
          {isCompleting ? (
            <CheckCircle2 className="h-6 w-6 text-green-500 drop-shadow-sm" />
          ) : (
            <Circle className="h-6 w-6 text-muted-foreground hover:text-primary transition-colors" />
          )}
        </button>

        <div className="flex-1 min-w-0 pr-12 flex flex-col h-full">
          {/* Title - Single line with ellipsis */}
          <h3
            className={cn(
              'font-bold text-lg leading-tight mb-2 transition-all duration-200',
              'truncate',
              isCompleting ? 'line-through text-muted-foreground' : 'text-foreground group-hover:text-primary'
            )}
            title={task.title}
          >
            {task.title}
          </h3>

          {/* Description - Max 2 lines with ellipsis */}
          {task.description && (
            <p
              className={cn(
                'text-sm text-muted-foreground mb-3 leading-relaxed',
                'line-clamp-2',
                isCompleting ? 'line-through' : ''
              )}
              title={task.description}
            >
              {task.description}
            </p>
          )}

          {/* Spacer to push badges to bottom */}
          <div className="flex-1" />

          {/* Badges - Always at bottom */}
          <div className="flex flex-wrap items-center gap-2 text-xs mt-auto">
            {task.dueDate && (
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-secondary/80 backdrop-blur-sm rounded-full border border-border/50 shadow-sm">
                <Clock className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                <span className="text-muted-foreground font-medium whitespace-nowrap">
                  {new Date(task.dueDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              </div>
            )}

            {task.priority && (
              <div className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-full capitalize font-semibold shadow-sm border',
                getPriorityColor(task.priority),
                task.priority === 'high' ? 'border-red-500/30' :
                task.priority === 'medium' ? 'border-yellow-500/30' :
                task.priority === 'low' ? 'border-green-500/30' :
                'border-gray-500/30'
              )}>
                <Flag className="h-3.5 w-3.5 flex-shrink-0" />
                <span className="whitespace-nowrap">{task.priority}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons - Always visible on hover */}
      <div className="absolute bottom-3 right-3 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onEdit(task.id)}
          className="h-9 w-9 p-0 rounded-xl transition-all duration-200 hover:bg-primary/10 hover:text-primary hover:scale-110"
          aria-label="Edit task"
        >
          <Edit3 className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(task.id)}
          className="h-9 w-9 p-0 text-destructive rounded-xl transition-all duration-200 hover:bg-destructive/10 hover:text-destructive hover:scale-110"
          aria-label="Delete task"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </motion.div>
  );
}


