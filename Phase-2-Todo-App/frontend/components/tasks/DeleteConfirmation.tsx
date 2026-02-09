import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { modalVariants } from '@/lib/animations';
import { cn } from '@/lib/utils';

interface DeleteConfirmationProps {
  isOpen: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  title: string;
  description?: string;
}

export function DeleteConfirmation({
  isOpen,
  onConfirm,
  onCancel,
  title,
  description
}: DeleteConfirmationProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="bg-background rounded-lg shadow-xl w-full max-w-md"
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-6 w-6 text-destructive mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold">Delete Task?</h3>
                    <p className="text-sm text-muted-foreground mt-1">{title}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onCancel}
                  aria-label="Close confirmation"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {description && (
                <p className="text-sm text-muted-foreground mb-6">
                  {description}
                </p>
              )}

              <div className="flex justify-end gap-3">
                <Button
                  variant="outline"
                  onClick={onCancel}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={onConfirm}
                >
                  Delete
                </Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}