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
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-muted mb-4">
        <ClipboardList className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
      {actionText && onAction && (
        <div className="mt-6">
          <Button onClick={onAction} className="rounded-full px-6">
            {actionText}
          </Button>
        </div>
      )}
    </motion.div>
  );
}