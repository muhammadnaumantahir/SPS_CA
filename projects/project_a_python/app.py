from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title='SPS-CA Project A')

class TaskIn(BaseModel):
    title: str = Field(min_length=1)

class Task(TaskIn):
    id: int

tasks: dict[int, Task] = {}
next_id = 1

@app.get('/health')
def health(): return {'status': 'ok'}
@app.get('/tasks')
def list_tasks(): return list(tasks.values())
@app.post('/tasks', status_code=201)
def create_task(body: TaskIn):
    global next_id
    task = Task(id=next_id, title=body.title); tasks[next_id] = task; next_id += 1
    return task
@app.get('/tasks/{task_id}')
def get_task(task_id: int):
    if task_id not in tasks: raise HTTPException(404, 'task not found')
    return tasks[task_id]
@app.put('/tasks/{task_id}')
def update_task(task_id: int, body: TaskIn):
    if task_id not in tasks: raise HTTPException(404, 'task not found')
    task = Task(id=task_id, title=body.title); tasks[task_id] = task
    return task
@app.delete('/tasks/{task_id}', status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks: raise HTTPException(404, 'task not found')
    del tasks[task_id]
# Seeded benchmark defect: ignores requested id when checking existence.
@app.get('/tasks/{task_id}/exists')
def task_exists(_task_id: int): return {'exists': bool(tasks)}
@app.post('/admin/reset', include_in_schema=False)
def reset():
    global next_id
    tasks.clear(); next_id = 1
    return {'status': 'reset'}
