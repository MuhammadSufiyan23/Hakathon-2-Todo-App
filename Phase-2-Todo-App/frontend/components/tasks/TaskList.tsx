import { AnimatePresence, motion } from 'framer-motion';
import { TaskCard } from '@/components/tasks/TaskCard';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  createdAt: string;
  updatedAt: string;
  userId: string;
  dueDate: string | null;
  priority: 'low' | 'medium' | 'high' | null;
}

interface TaskListProps {
  tasks: Task[];
  viewMode?: 'grid' | 'list';
  onUpdate: (updatedTask: Task) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string) => void;
  onToggleCompletion?: (id: string) => Promise<void>; // Async for await
}

export function TaskList({ tasks, viewMode = 'grid', onUpdate, onToggleCompletion, onDelete, onEdit }: TaskListProps) {
  const handleToggle = async (id: string, newCompleted: boolean) => {
    console.log(`[TaskList] Toggle started for ${id} to ${newCompleted}`);

    const task = tasks.find(t => t.id === id);
    if (!task) return;

    // Optimistic update – immediate state change
    onUpdate({ ...task, completed: newCompleted });
    console.log(`[TaskList] Optimistic update applied for ${id} to ${newCompleted}`);

    try {
      if (onToggleCompletion) {
        await onToggleCompletion(id);
        console.log(`[TaskList] Toggle success for ${id}`);
      } else {
        console.warn('[TaskList] No onToggleCompletion provided');
      }
      // No rollback on success – keep optimistic change
    } catch (error: any) {
      console.error(`[TaskList] Toggle failed for ${id}:`, error);
      // Rollback on error
      onUpdate({ ...task, completed: task.completed });
      console.log(`[TaskList] Rollback applied for ${id} to ${task.completed}`);
      throw error; // Bubble error to TaskCard
    }
  };

  return (
    <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-3'}>
      <AnimatePresence mode="sync">  // Changed mode to "sync" to prevent disappear
        {tasks.map((task, index) => {
          console.log('[TaskList] Passing task to card:', { dueDate: task.dueDate, priority: task.priority });
          return (
          <motion.div
            key={task.id} // Key stable
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <TaskCard
              task={task}
              index={index}
              onToggle={handleToggle}
              onEdit={onEdit}
              onDelete={onDelete}
              viewMode={viewMode}
            />
          </motion.div>
        )})}
      </AnimatePresence>
    </div>
  );
}