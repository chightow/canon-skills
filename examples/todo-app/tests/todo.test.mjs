import test from 'node:test';
import assert from 'node:assert/strict';
import {
  addTodo,
  createTodo,
  remainingCount,
  toggleTodo
} from '../src/app.js';

test('createTodo trims titles and creates stable ids', () => {
  assert.deepEqual(createTodo('  Buy milk  ', 1000), {
    id: 'todo-1000-buy-milk',
    title: 'Buy milk',
    done: false,
    createdAt: 1000
  });
});

test('blank todo titles are ignored', () => {
  const items = [{ id: 'todo-1', title: 'Existing', done: false }];
  assert.equal(createTodo('   ', 1000), null);
  assert.equal(addTodo(items, '   ', 1000), items);
});

test('todos can be added and toggled complete', () => {
  let items = [];
  items = addTodo(items, 'Ship docs', 1);
  items = addTodo(items, 'Open sprint-check', 2);

  assert.equal(remainingCount(items), 2);

  items = toggleTodo(items, 'todo-1-ship-docs');
  assert.equal(remainingCount(items), 1);
  assert.equal(items[0].done, true);

  items = toggleTodo(items, 'todo-1-ship-docs');
  assert.equal(remainingCount(items), 2);
  assert.equal(items[0].done, false);
});
