---
id: 2
title: "Fix Tasks Undefined Error"
stage: "red"
date_iso: "2026-01-16"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "master"
user: "king"
command: "/sp.implement"
labels: ["tasks", "error-handling", "ui"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "frontend/app/tasks/all/page.tsx"
  - "frontend/app/tasks/pending/page.tsx"
  - "frontend/app/tasks/completed/page.tsx"
tests_yaml: []
---

# Fix Tasks Undefined Error

## Outcome
Fixed "tasks is undefined" TypeError crash on /tasks/all, /tasks/pending, and /tasks/completed pages by implementing safe API response handling and proper conditional checks.

## Evaluation
- Applied safe fallback handling: response?.tasks || response || [] to prevent undefined errors
- Added proper error type handling with error message extraction
- Ensured all pages safely check if tasks exist before accessing length property
- Maintained existing loading and error UI states
- All three task list pages now handle API failures gracefully without crashing

## Prompt Text
```
IMPORTANT: Do NOT touch, rewrite, or change signup, signin, auth pages, login, auth-client.ts, api.ts, or any authentication-related code. Signup and signin are already working perfectly – leave them 100% untouched.

Focus ONLY on fixing the "tasks is undefined" TypeError crash on /tasks/all, /tasks/pending, and /tasks/completed pages.

Current error:
- Unhandled Runtime Error: TypeError: can't access property "length", tasks is undefined
- Source: app/tasks/[all|pending|completed]/page.tsx (line ~69): tasks.length === 0 ? <EmptyState />
- Cause: apiClient.getTasks() call fails silently or returns undefined/null, and page uses tasks.length without checking if tasks exists or is array.

Fix ONLY in the three task list pages:
- /app/tasks/all/page.tsx
- /app/tasks/pending/page.tsx
- /app/tasks/completed/page.tsx

Required changes (same pattern for all three):
- Add useState for tasks, loading, error
- Use useEffect to fetch tasks with try/catch
- Use apiClient.getTasks('all'), ('pending'), ('completed') respectively
- Add loading UI (spinner or text)
- Add error UI with Retry button
- If tasks undefined or not array → show error or empty state
- Only render EmptyState if tasks is array AND length === 0
- Example structure:
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getTasks('all'); // change 'all' for pending/completed
        setTasks(response.tasks || response || []); // safe fallback
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
    <div>
      {/* existing header/sidebar */}
      {tasks.length === 0 ? (
        <EmptyState title="No tasks..." ... />
      ) : (
        // render task cards
      )}
    </div>
  );

Output ONLY:
- Full updated code for app/tasks/all/page.tsx (with getTasks('all'))
- Full updated code for app/tasks/pending/page.tsx (with getTasks('pending'))
- Full updated code for app/tasks/completed/page.tsx (with getTasks('completed'))
- Instructions: "Replace the three page.tsx files with these codes. Restart frontend (npm run dev). Login → go to /tasks/all, /pending, /completed – no crash, loading/error handle hoga, empty = EmptyState."

Do NOT output any signup/signin code, auth-client, api.ts, backend, or unrelated files.

Execute now – fix ONLY the undefined tasks crash on list pages!
```

## Response Text
Fixed the "tasks is undefined" TypeError crash by:
1. Updating useEffect hooks in all three task list pages to safely handle API responses with fallbacks: response?.tasks || response || []
2. Adding proper error handling with type annotation (err: any) and error message extraction
3. Adding safeguards to conditional rendering to check if tasks exists before accessing length property
4. Maintaining all existing functionality while preventing crashes from undefined tasks