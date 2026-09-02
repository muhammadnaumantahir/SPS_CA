import request from 'supertest';
import { app, resetTasks } from '../src/app';

describe('Task API contract', () => {
  beforeEach(() => resetTasks());

  it('supports health and CRUD', async () => {
    expect((await request(app).get('/health')).body).toEqual({ status: 'ok' });
    const created = await request(app).post('/tasks').send({ title: 'write tests' }).expect(201);
    expect(created.body.id).toBe(1);
    expect((await request(app).get('/tasks/1')).body.title).toBe('write tests');
    expect((await request(app).put('/tasks/1').send({ title: 'better tests' })).body.title).toBe('better tests');
    await request(app).delete('/tasks/1').expect(204);
    await request(app).get('/tasks/1').expect(404);
  });

  it('keeps task ids distinct', async () => {
    await request(app).post('/tasks').send({ title: 'first' }).expect(201);
    const second = await request(app).post('/tasks').send({ title: 'second' }).expect(201);
    expect((await request(app).get(`/tasks/${second.body.id}`)).body.id).toBe(second.body.id);
  });

  it('rejects empty titles', async () => {
    await request(app).post('/tasks').send({ title: '' }).expect(400);
  });
});
