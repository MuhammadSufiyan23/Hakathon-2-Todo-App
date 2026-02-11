import React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { PriorityLevel } from '@/src/types/task';

interface PrioritySelectorProps {
  value?: PriorityLevel;
  onChange: (value: PriorityLevel | undefined) => void;
  placeholder?: string;
  className?: string;
}

export function PrioritySelector({
  value,
  onChange,
  placeholder = 'Select priority',
  className = ''
}: PrioritySelectorProps) {
  const handleValueChange = (newValue: string) => {
    if (newValue === 'none') {
      onChange(undefined);
    } else {
      onChange(newValue as PriorityLevel);
    }
  };

  return (
    <Select
      value={value || 'none'}
      onValueChange={handleValueChange}
    >
      <SelectTrigger className={className}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="none">No priority</SelectItem>
        <SelectItem value="low">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span>Low</span>
          </div>
        </SelectItem>
        <SelectItem value="medium">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-yellow-500" />
            <span>Medium</span>
          </div>
        </SelectItem>
        <SelectItem value="high">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span>High</span>
          </div>
        </SelectItem>
      </SelectContent>
    </Select>
  );
}
