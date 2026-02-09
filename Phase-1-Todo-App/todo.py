
#!/usr/bin/env python3
"""📝 Todo List Manager - Phase I Console Application.

A simple in-memory todo list manager with CRUD operations.
"""

import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

tasks: list[dict] = []
next_id: int = 1


def get_task_by_id(task_id: int) -> dict | None:
    """🔎 Find and return a task by ID, or None if not found."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def display_menu() -> None:
    """📋 Print the main menu options."""
    print("\n📋 Main Menu")
    print("1️⃣  Add task")
    print("2️⃣  View all tasks")
    print("3️⃣  Update task")
    print("4️⃣  Delete task")
    print("5️⃣  Mark task complete / incomplete")
    print("6️⃣  Exit 🚪")


def add_task() -> None:
    """➕ Add New Task."""
    global next_id

    print("\n➕ --- Add New Task ---")

    title = input("✏️  Enter task title (required): ").strip()
    if not title:
        print("❌ Error: Title cannot be empty.")
        return

    description = input("🧾 Enter task description (optional): ")

    task = {
        "id": next_id,
        "title": title,
        "description": description,
        "completed": False,
    }
    tasks.append(task)
    print(f"✅ Task {next_id} added successfully.")
    next_id += 1


def view_tasks() -> None:
    """📖 View All Tasks."""
    print("\n📖 --- All Tasks ---")

    if not tasks:
        print("📭 No tasks yet.")
        return

    for task in tasks:
        status = "✔️ Completed" if task["completed"] else "⏳ Incomplete"
        print(f"{task['id']}. {task['title']} [{status}]")
        if task["description"]:
            print(f"    🧾 {task['description']}")


def update_task() -> None:
    """✏️ Update Existing Task."""
    print("\n✏️ --- Update Task ---")

    try:
        task_id = int(input("🔢 Enter task ID to update: ").strip())
    except ValueError:
        print("❌ Error: Please enter a valid number.")
        return

    task = get_task_by_id(task_id)
    if not task:
        print(f"❌ Error: No task found with ID {task_id}.")
        return

    print(f"📌 Current title: {task['title']}")
    print(f"🧾 Current description: {task['description']}")

    new_title = input("✏️  New title (leave blank to keep current): ").strip()
    if new_title:
        task["title"] = new_title

    new_desc = input("🧾 New description (leave blank to keep current): ").strip()
    if new_desc:
        task["description"] = new_desc

    print(f"✅ Task {task_id} updated successfully.")


def delete_task() -> None:
    """🗑️ Delete Task."""
    print("\n🗑️ --- Delete Task ---")

    try:
        task_id = int(input("🔢 Enter task ID to delete: ").strip())
    except ValueError:
        print("❌ Error: Please enter a valid number.")
        return

    task = get_task_by_id(task_id)
    if not task:
        print(f"❌ Error: No task found with ID {task_id}.")
        return

    tasks.remove(task)
    print(f"🗑️ Task {task_id} deleted successfully.")


def toggle_task_completion() -> None:
    """🔁 Mark Task Complete or Incomplete with Clear UX."""
    print("\n🔁 --- Change Task Status ---")

    try:
        task_id = int(input("🔢 Enter task ID: ").strip())
    except ValueError:
        print("❌ Error: Please enter a valid number.")
        return

    task = get_task_by_id(task_id)
    if not task:
        print(f"❌ Error: No task found with ID {task_id}.")
        return

    current_status = "✔️ Completed" if task["completed"] else "⏳ Incomplete"
    print(f"\n📌 Task: {task['title']}")
    print(f"📌 Current Status: {current_status}")

    if task["completed"]:
        confirm = input("❓ Mark this task as INCOMPLETE? (y/n): ").lower()
        if confirm == "y":
            task["completed"] = False
            print("⏳ Task marked as INCOMPLETE.")
        else:
            print("ℹ️ No changes made.")
    else:
        confirm = input("❓ Mark this task as COMPLETE? (y/n): ").lower()
        if confirm == "y":
            task["completed"] = True
            print("🎉 Task marked as COMPLETE.")
        else:
            print("ℹ️ No changes made.")


def main() -> None:
    """🚀 Application Entry Point."""
    print("👋 Welcome to the Todo List Manager!")

    while True:
        display_menu()
        choice = input("👉 Enter your choice (1-6): ").strip()

        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            update_task()
        elif choice == "4":
            delete_task()
        elif choice == "5":
            toggle_task_completion()
        elif choice == "6":
            print("👋 Goodbye! Stay productive 💪")
            break
        else:
            print("⚠️ Invalid choice. Please select between 1 and 6.")


if __name__ == "__main__":
    main()
