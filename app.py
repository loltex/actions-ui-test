from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)

tasks = []
next_id = 1

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>test todo app</title>
  <style>
    body { max-width: 700px; margin: 40px auto; padding: 0 16px;
           font: 16px sans-serif; color: #222; }
    form, .toolbar, .stats { display: flex; gap: 10px; flex-wrap: wrap;
                             align-items: center; margin: 16px 0; }
    input, select, button { padding: 8px; }
    input[type="search"] { flex: 1; min-width: 180px; }
    .stats { color: #555; }
    .task { display: flex; justify-content: space-between; gap: 12px;
            align-items: center; padding: 12px 0; border-top: 1px solid #ddd; }
    .task-actions { display: flex; gap: 8px; }
    .completed .task-text { text-decoration: line-through; color: #666; }
    .priority { color: #555; font-size: 0.9em; }
    #empty-message { color: #666; }
    button[aria-pressed="true"] { font-weight: bold; }
  </style>
</head>
<body>
  <h1>test todo app</h1>
  <p>Add tasks and their priority.</p>

  <form action="/tasks" method="post">
    <label for="task-input">Task</label>
    <input id="task-input" name="task" required placeholder="e.g. Water the plants">

    <label for="priority-select">Priority</label>
    <select id="priority-select" name="priority">
      <option>Low</option>
      <option selected>Medium</option>
      <option>High</option>
    </select>

    <button id="add-task" type="submit">Add task</button>
  </form>

  <div class="stats" aria-label="Task totals">
    <span>Total: <strong id="total-count">{{ tasks|length }}</strong></span>
    <span>Active: <strong id="active-count">{{ active_count }}</strong></span>
    <span>Completed: <strong id="completed-count">{{ completed_count }}</strong></span>
  </div>

  <div class="toolbar">
    <label for="search-input">Search</label>
    <input id="search-input" type="search" placeholder="Find a task">

    <button type="button" data-filter="all" aria-pressed="true">All</button>
    <button type="button" data-filter="active" aria-pressed="false">Active</button>
    <button type="button" data-filter="completed" aria-pressed="false">Completed</button>
  </div>

  <ul id="task-list">
    {% for task in tasks %}
      <li class="task {{ 'completed' if task.completed else '' }}"
          data-testid="task-item"
          data-status="{{ 'completed' if task.completed else 'active' }}"
          data-task-text="{{ task.text|lower }}">
        <div>
          <span class="task-text">{{ task.text }}</span>
          <span class="priority">({{ task.priority }})</span>
        </div>

        <div class="task-actions">
          <form action="/tasks/{{ task.id }}/toggle" method="post">
            <button class="toggle-task" type="submit">
              {{ 'Undo' if task.completed else 'Complete' }}
            </button>
          </form>
          <form action="/tasks/{{ task.id }}/delete" method="post">
            <button class="delete-task" type="submit">Delete</button>
          </form>
        </div>
      </li>
    {% endfor %}
  </ul>

  <p id="empty-message" {% if tasks %}hidden{% endif %}>No tasks yet. Add one above.</p>

  <script>
    const searchInput = document.getElementById("search-input");
    const filterButtons = document.querySelectorAll("[data-filter]");
    const taskItems = document.querySelectorAll("[data-testid='task-item']");
    let currentFilter = "all";

    function updateVisibleTasks() {
      const query = searchInput.value.trim().toLowerCase();

      taskItems.forEach((item) => {
        const matchesFilter =
          currentFilter === "all" || item.dataset.status === currentFilter;
        const matchesSearch = item.dataset.taskText.includes(query);
        item.hidden = !(matchesFilter && matchesSearch);
      });
    }

    searchInput.addEventListener("input", updateVisibleTasks);

    filterButtons.forEach((button) => {
      button.addEventListener("click", () => {
        currentFilter = button.dataset.filter;
        filterButtons.forEach((other) => {
          other.setAttribute(
            "aria-pressed",
            String(other === button)
          );
        });
        updateVisibleTasks();
      });
    });
  </script>
</body>
</html>
"""


@app.get("/")
def home():
    active_count = sum(not task["completed"] for task in tasks)
    completed_count = sum(task["completed"] for task in tasks)
    return render_template_string(
        PAGE,
        tasks=tasks,
        active_count=active_count,
        completed_count=completed_count,
    )


@app.post("/tasks")
def add_task():
    global next_id

    text = request.form.get("task", "").strip()
    priority = request.form.get("priority", "Medium")
    if priority not in {"Low", "Medium", "High"}:
        priority = "Medium"

    if text:
        tasks.append({
            "id": next_id,
            "text": text,
            "priority": priority,
            "completed": False,
        })
        next_id += 1

    return redirect("/")


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            break
    return redirect("/")


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    tasks[:] = [task for task in tasks if task["id"] != task_id]
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
