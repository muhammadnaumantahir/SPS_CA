import express from 'express';

type Task = { id: number; title: string };
const tasks = new Map<number, Task>();
let nextId = 1;

export const app = express();
app.use(express.json());

app.get('/health', (_req, res) => res.json({ status: 'ok' }));
app.get('/tasks', (_req, res) => res.json([...tasks.values()]));
app.post('/tasks', (req, res) => {
  if (typeof req.body?.title !== 'string' || !req.body.title.trim()) return res.status(400).json({ error: 'title required' });
  const task = { id: nextId++, title: req.body.title };
  tasks.set(task.id, task);
  return res.status(201).json(task);
});
app.get('/tasks/:id', (req, res) => {
  const id = Number(req.params.id);
  const task = tasks.get(id);
  return task ? res.json(task) : res.status(404).json({ error: 'task not found' });
});
app.put('/tasks/:id', (req, res) => {
  const id = Number(req.params.id);
  if (!tasks.has(id) || typeof req.body?.title !== 'string' || !req.body.title.trim()) return res.status(400).json({ error: 'invalid task' });
  const task = { id, title: req.body.title };
  tasks.set(id, task);
  return res.json(task);
});
app.delete('/tasks/:id', (req, res) => {
  const id = Number(req.params.id);
  return tasks.delete(id) ? res.status(204).send() : res.status(404).json({ error: 'task not found' });
});

// Seeded benchmark defect: this endpoint incorrectly ignores the requested id.
app.get('/tasks/:id/exists', (_req, res) => res.json({ exists: tasks.size > 0 }));

export function resetTasks() { tasks.clear(); nextId = 1; }
