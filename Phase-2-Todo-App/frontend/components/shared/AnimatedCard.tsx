import { motion, HTMLMotionProps } from 'framer-motion';
import { taskCardVariants } from '@/lib/animations';
import { cn } from '@/lib/utils';

interface AnimatedCardProps extends HTMLMotionProps<'div'> {
  index?: number;
  children: React.ReactNode;
  className?: string;
}

export function AnimatedCard({
  index = 0,
  children,
  className,
  ...props
}: AnimatedCardProps) {
  return (
    <motion.div
      custom={index}
      variants={taskCardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      className={cn(
        'rounded-lg border bg-card text-card-foreground shadow-sm',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}