import React from 'react';
import { Badge } from '@/components/ui/badge';
import type { PriorityLevel } from '@/src/types/task';

interface PriorityBadgeProps {
  priority?: PriorityLevel;
  className?: string;
}

export function PriorityBadge({ priority, className = '' }: PriorityBadgeProps) {
  if (!priority) {
    return null;
  }

  const priorityConfig = {
    high: {
      label: 'High',
      className: 'bg-red-100 text-red-800 hover:bg-red-200 border-red-300'
    },
    medium: {
      label: 'Medium',
      className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-300'
    },
    low: {
      label: 'Low',
      className: 'bg-green-100 text-green-800 hover:bg-green-200 border-green-300'
    }
  };

  const config = priorityConfig[priority];

  return (
    <Badge
      variant="outline"
      className={`${config.className} ${className} font-medium`}
    >
      {config.label}
    </Badge>
  );
}
