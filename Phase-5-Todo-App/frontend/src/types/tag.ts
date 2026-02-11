// Tag types for task organization

export interface Tag {
  id: number;
  name: string;
  user_id: string;
  color?: string; // Hex color code (e.g., '#FF5733')
  created_at: string; // ISO 8601 datetime string

  // Optional: task count (populated by backend when listing tags)
  task_count?: number;
}

// Tag creation payload
export interface TagCreate {
  name: string;
  color?: string;
}

// Tag update payload
export interface TagUpdate {
  name?: string;
  color?: string;
}
