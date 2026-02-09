---
id: 3
title: "Fix Dashboard Request Error"
stage: "red"
date_iso: "2026-01-16"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "master"
user: "king"
command: "/sp.implement"
labels: ["dashboard", "error-handling", "ui"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "frontend/app/dashboard/page.tsx"
tests_yaml: []
---

# Fix Dashboard Request Error

## Outcome
Fixed "Failed to load tasks: can't access property 'request', this is undefined" error on dashboard page by replacing react-query hooks with direct useEffect approach and implementing safe API response handling.

## Evaluation
- Bypassed problematic react-query hooks that caused the 'request' property error
- Implemented direct useEffect approach with proper state management
- Added safe API response handling: response?.tasks || response || [] fallback
- Added proper error handling with error message extraction and retry functionality
- Maintained all existing dashboard functionality while preventing crashes
- Loading states, error handling, and UI elements preserved

## Prompt Text
```
IMPORTANT: Do NOT touch, rewrite, or change signup, signin, auth pages, login, auth-client.ts, api.ts, or any authentication-related code. Signup and signin are working perfectly – leave them 100% untouched.

Focus ONLY on fixing the "Failed to load tasks: can't access property "request", this is undefined" error on dashboard page (/app/dashboard/page.tsx) and ensure task list pages (all/pending/completed) are robust.

Current error on dashboard:
- Failed to load tasks: can't access property "request", this is undefined
- Cause: fetch call fails, response/request is undefined, code tries to access response.request or similar without check.

Fix ONLY in:
- /app/dashboard/page.tsx (main dashboard tasks load logic)

Required changes:
- Use useState for tasks, loading, error
- useEffect to fetch tasks with try/catch
- Use apiClient.getTasks('all') or dashboard-specific fetch
- NEVER access response.request or any undefined property
- Safe fallback: tasks = response?.tasks || response || []
- Loading UI: spinner/text
- Error UI: message + Retry button
- If tasks undefined or not array → show error or empty state

Example structure:
const [tasks, setTasks] = useState<Task[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getTasks('all');
      setTasks(response?.tasks || response || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load tasks');
      toast.error(err.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };
  fetchTasks();
}, []);

if (loading) return <div className="flex justify-center items-center h-64">Loading tasks...</div>;

if (error) return (
  <div className="text-center p-8">
    <p className="text-red-500 mb-4">{error}</p>
    <Button onClick={() => window.location.reload()}>Retry</Button>
  </div>
);

return (
  <div className="flex h-screen">
    {/* sidebar */}
    <div className="flex-1 p-6">
      {/* header */}
      {tasks.length === 0 ? (
        <EmptyState title="No tasks yet" description="Start adding tasks!" actionText="New Task" onAction={() => router.push('/tasks/new')} />
      ) : (
        // render task cards or TaskList component
        tasks.map(task => <TaskCard key={task.id} task={task} />)
      )}
    </div>
  </div>
);

Output ONLY:
- Full updated code for app/dashboard/page.tsx (with safe fetch and error handling)
- Instructions: "Replace app/dashboard/page.tsx with this code. Restart frontend (npm run dev). Login → go to dashboard – no crash, loading/error handle hoga, tasks load if any or show EmptyState."

Do NOT output signup/signin code, api.ts, backend, task list pages (all/pending/completed), or unrelated files.

Execute now – fix ONLY the undefined "request" crash on dashboard!
```

## Response Text
Fixed the "Failed to load tasks: can't access property 'request', this is undefined" error by:
1. Replacing react-query hooks with direct useEffect approach to bypass the problematic 'request' property access
2. Adding proper state management for tasks, loading, and error states
3. Implementing safe API response handling with fallbacks: response?.tasks || response || []
4. Adding proper error handling with type annotation and error message extraction
5. Maintaining all existing dashboard functionality while preventing crashes