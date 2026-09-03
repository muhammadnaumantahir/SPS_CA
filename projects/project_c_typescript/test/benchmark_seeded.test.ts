import request from 'supertest';
import { describe, beforeEach, it, expect } from 'vitest';
import { app, resetTasks } from '../src/app';

describe('Seeded self-programming benchmark', () => {
  beforeEach(() => resetTasks());

  it('preserves the intentionally seeded exists defect', async () => {
    await request(app).post('/tasks').send({ title: 'one' }).expect(201);
    expect((await request(app).get('/tasks/999/exists')).body.exists).toBe(true);
  });
});
