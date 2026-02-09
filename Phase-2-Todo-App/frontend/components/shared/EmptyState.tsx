import { motion } from 'framer-motion';
import { ClipboardList } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { fadeIn } from '@/lib/animations';

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
}

export function EmptyState({
  title,
  description,
  actionText,
  onAction
}: EmptyStateProps) {
  return (
    <motion.div
      className="text-center py-12"
      initial="hidden"
      animate="visible"
      variants={fadeIn}
    >
      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-muted">
        <ClipboardList className="h-10 w-10 text-muted-foreground" />
      </div>
      <h3 className="mt-4 text-xl font-semibold">{title}</h3>
      <p className="mt-2 text-muted-foreground">{description}</p>
      {actionText && onAction && (
        <div className="mt-6">
          <Button onClick={onAction}>
            {actionText}
          </Button>
        </div>
      )}
    </motion.div>
  );
}