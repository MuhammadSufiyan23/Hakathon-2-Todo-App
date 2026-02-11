import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getTasks,
  getTaskById,
  createTask,
  updateTask,
  deleteTask,
  toggleTaskCompletion,
  type Task,
  type GetTasksResponse,
  type CreateTaskResponse,
  type UpdateTaskResponse,
  type DeleteTaskResponse,
} from '@/lib/api';

// Define custom hooks for task operations
export function useTasks(status?: 'all' | 'pending' | 'completed', sortBy?: 'createdAt' | 'title' | 'dueDate', sortOrder?: 'asc' | 'desc') {
  return useQuery<GetTasksResponse, Error>({
    queryKey: ['tasks', status, sortBy, sortOrder],
    queryFn: () => getTasks(status, sortBy, sortOrder),
  });
}

export function useTask(id: string) {
  return useQuery<Task, Error>({
    queryKey: ['task', id],
    queryFn: () => getTaskById(id),
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation<CreateTaskResponse, Error, Partial<Task>>({
    mutationFn: (taskData) => createTask(taskData as any), // Cast to any to satisfy type requirements temporarily
    onSuccess: () => {
      // Invalidate and refetch all tasks
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation<UpdateTaskResponse, Error, { id: string; data: Partial<Task> }>({
    mutationFn: ({ id, data }) => updateTask(id, data),
    onSuccess: () => {
      // Invalidate and refetch all tasks
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      // Also invalidate specific task if needed
      queryClient.invalidateQueries({ queryKey: ['task'] });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation<DeleteTaskResponse, Error, string>({
    mutationFn: (id) => deleteTask(id),
    onSuccess: () => {
      // Invalidate and refetch all tasks
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

export function useToggleTaskCompletion() {
  const queryClient = useQueryClient();

  return useMutation<UpdateTaskResponse, Error, string>({
    mutationFn: (id) => toggleTaskCompletion(id),
    onSuccess: () => {
      // Invalidate and refetch all tasks
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}