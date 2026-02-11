// Reminder types for task notifications

export type ReminderStatus = 'pending' | 'sent' | 'failed';

export interface Reminder {
  id: number;
  task_id: string;
  user_id: string;
  remind_at: string; // ISO 8601 datetime string
  status: ReminderStatus;
  sent_at?: string; // ISO 8601 datetime string
  created_at: string; // ISO 8601 datetime string
}

// Reminder creation payload
export interface ReminderCreate {
  task_id: string;
  remind_at: string; // ISO 8601 datetime string
}

// Reminder update payload
export interface ReminderUpdate {
  remind_at?: string;
  status?: ReminderStatus;
}
