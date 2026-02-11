import { motion } from 'framer-motion';
import { CheckCircle, Circle } from 'lucide-react';
import { springCheck } from '@/lib/animations';

interface TaskCompletionAnimationProps {
  completed: boolean;
  isLoading?: boolean;
  size?: number;
}

export function TaskCompletionAnimation({
  completed,
  isLoading = false,
  size = 20,
}: TaskCompletionAnimationProps) {
  return (
    <motion.div
      variants={springCheck}
      initial="initial"
      animate={completed ? 'checked' : 'animate'}
      whileTap="tap"
      style={{ opacity: isLoading ? 0.5 : 1 }}
      transition={{ duration: 0.2 }}
    >
      {completed ? (
        <CheckCircle
          className="text-emerald-500"
          size={size}
          fill="currentColor"
        />
      ) : (
        <Circle
          className="text-gray-300 dark:text-gray-600"
          size={size}
          fill="none"
          strokeWidth={2}
        />
      )}
    </motion.div>
  );
}





