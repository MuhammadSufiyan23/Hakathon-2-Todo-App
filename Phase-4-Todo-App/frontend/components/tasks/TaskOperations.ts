import { useCreateTask, useUpdateTask, useDeleteTask, useToggleTaskCompletion } from '@/hooks/use-tasks';
import type { Task } from '@/lib/api';

export interface TaskOperationResult {
  success: boolean;
  message: string;
  data?: any;
}

export class TaskOperations {
  static useCreateTask() {
    return useCreateTask();
  }

  static useUpdateTask() {
    return useUpdateTask();
  }

  static useDeleteTask() {
    return useDeleteTask();
  }

  static useToggleTaskCompletion() {
    return useToggleTaskCompletion();
  }

  // Helper methods for common operations
  static async createTask(taskData: Omit<Task, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<TaskOperationResult> {
    try {
      // This would typically call the API directly
      // For now, we'll just return a mock result
      return {
        success: true,
        message: 'Task created successfully',
        data: {
          id: Date.now().toString(),
          ...taskData,
          completed: false,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to create task',
      };
    }
  }

  static async updateTask(id: string, taskData: Partial<Task>): Promise<TaskOperationResult> {
    try {
      // This would typically call the API directly
      return {
        success: true,
        message: 'Task updated successfully',
        data: {
          id,
          ...taskData,
          updatedAt: new Date().toISOString(),
        }
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to update task',
      };
    }
  }

  static async deleteTask(id: string): Promise<TaskOperationResult> {
    try {
      // This would typically call the API directly
      return {
        success: true,
        message: 'Task deleted successfully',
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to delete task',
      };
    }
  }

  static async toggleTaskCompletion(id: string): Promise<TaskOperationResult> {
    try {
      // This would typically call the API directly
      return {
        success: true,
        message: 'Task completion status updated',
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Failed to toggle task completion',
      };
    }
  }
}