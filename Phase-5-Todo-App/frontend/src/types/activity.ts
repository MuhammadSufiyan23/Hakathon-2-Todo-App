// Activity log types for audit trail

export type ActivityAction =
  | 'task_created'
  | 'task_updated'
  | 'task_deleted'
  | 'task_completed'
  | 'tag_added'
  | 'tag_removed'
  | 'reminder_set'
  | 'reminder_sent';

export interface ActivityLog {
  id: number;
  user_id: string;
  action: ActivityAction;
  task_id?: string;
  details?: string; // JSON string with additional details
  created_at: string; // ISO 8601 datetime string
}

// Parsed activity details (when details is JSON)
export interface ActivityDetails {
  title?: string;
  old_value?: any;
  new_value?: any;
  tag_name?: string;
  [key: string]: any; // Allow additional properties
}
