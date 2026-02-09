'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { TaskForm } from '@/components/tasks/TaskForm';

export default function NewTaskPage() {
  const router = useRouter();
  const [showForm, setShowForm] = useState(true);

  const handleSubmit = (task: any) => {
    // In a real app, this would be an API call
    console.log('Created task:', task);

    // Navigate back to dashboard after creation
    router.push('/dashboard');
  };

  const handleClose = () => {
    router.push('/dashboard');
  };

  return (
    <div className="container mx-auto py-6">
      <h1 className="text-2xl font-bold mb-6">Create New Task</h1>
      {showForm && (
        <TaskForm
          onSubmit={handleSubmit}
          onClose={handleClose}
        />
      )}
    </div>
  );
}