// Task-related types for Phase III-IV Advanced Features

export type PriorityLevel = 'low' | 'medium' | 'high';
export type RecurrenceRule = 'daily' | 'weekly' | 'monthly';

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;

  // Phase III-IV new fields
  priority?: PriorityLevel;
  due_date?: string; // ISO 8601 datetime string
  is_recurring: boolean;
  recurrence_rule?: RecurrenceRule;
  completed_at?: string; // ISO 8601 datetime string
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string

  // Tags will be populated via JOIN in backend
  tags?: Tag[];
}

// Import Tag type (will be defined in tag.ts)
import type { Tag } from './tag';

// Task creation payload (subset of Task)
export interface TaskCreate {
  title: string;
  description?: string;
  priority?: PriorityLevel;
  due_date?: string;
  is_recurring?: boolean;
  recurrence_rule?: RecurrenceRule;
}

// Task update payload (all fields optional except id)
export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: PriorityLevel;
  due_date?: string;
  is_recurring?: boolean;
  recurrence_rule?: RecurrenceRule;
}

// Task filter parameters
export interface TaskFilters {
  search?: string;
  priority?: PriorityLevel;
  completed?: boolean;
  tag?: string[];
  sort_by?: 'created_at' | 'due_date' | 'priority' | 'updated_at';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  offset?: number;
}
