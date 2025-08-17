// // Fetch all todos when the page loads
// document.addEventListener('DOMContentLoaded', fetchTodos);

// // Add event listener for Enter key in input field
// document.getElementById('todoInput').addEventListener('keypress', function(e) {
//     if (e.key === 'Enter') {
//         addTodo();
//     }
// });

// async function fetchTodos() {
//     try {
//         const response = await fetch('/api/todos');
//         const todos = await response.json();
//         displayTodos(todos);
//     } catch (error) {
//         console.error('Error fetching todos:', error);
//     }
// }

// function displayTodos(todos) {
//     const todoList = document.getElementById('todoList');
//     todoList.innerHTML = '';
    
//     todos.forEach(todo => {
//         const todoItem = document.createElement('div');
//         todoItem.className = `todo-item ${todo.completed ? 'completed' : ''}`;
//         todoItem.innerHTML = `
//             <div class="todo-content">
//                 <span class="todo-text">${todo.title}</span>
//                 <span class="todo-time">Created: ${todo.created_at}</span>
//             </div>
//             <div class="todo-actions">
//                 <button class="toggle" onclick="toggleTodo(${todo.id})">
//                     ${todo.completed ? 'Undo' : 'Complete'}
//                 </button>
//                 <button class="delete" onclick="deleteTodo(${todo.id})">Delete</button>
//             </div>
//         `;
//         todoList.appendChild(todoItem);
//     });
// }

// async function addTodo() {
//     const input = document.getElementById('todoInput');
//     const title = input.value.trim();
    
//     if (!title) return;
    
//     try {
//         const response = await fetch('/api/todos', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ title }),
//         });
        
//         if (response.ok) {
//             input.value = '';
//             fetchTodos();
//         } else {
//             const errorData = await response.json();
//             console.error('Failed to add todo:', errorData);
//             if (response.status === 401) {
//                 // If unauthorized, redirect to login
//                 window.location.href = '/login';
//             } else {
//                 alert('Failed to add todo: ' + (errorData.message || 'Unknown error'));
//             }
//         }
//     } catch (error) {
//         console.error('Error adding todo:', error);
//         alert('Failed to add todo. Please try again.');
//     }
// }

// async function deleteTodo(id) {
//     try {
//         const response = await fetch(`/api/todos/${id}`, {
//             method: 'DELETE',
//         });
        
//         if (response.ok) {
//             fetchTodos();
//         }
//     } catch (error) {
//         console.error('Error deleting todo:', error);
//     }
// }

// async function toggleTodo(id) {
//     try {
//         const response = await fetch(`/api/todos/${id}`, {
//             method: 'PUT',
//         });
        
//         if (response.ok) {
//             fetchTodos();
//         }
//     } catch (error) {
//         console.error('Error toggling todo:', error);
//     }
// } 

// Run when page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchTodos();

    // Add button click
    document.getElementById('addBtn').addEventListener('click', addTodo);

    // Enter key in input
    document.getElementById('todoInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addTodo();
        }
    });
});

// Fetch all todos
async function fetchTodos() {
    try {
        const response = await fetch('/api/todos');
        if (!response.ok) throw new Error("Failed to fetch todos");
        const todos = await response.json();
        displayTodos(todos);
    } catch (error) {
        console.error('Error fetching todos:', error);
    }
}

// Render todos
function displayTodos(todos) {
    const todoList = document.getElementById('todoList');
    todoList.innerHTML = '';

    if (todos.length === 0) {
        todoList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <p>No tasks yet. Add one to get started!</p>
            </div>
        `;
        return;
    }

    todos.forEach(todo => {
        const todoItem = document.createElement('div');
        todoItem.className = `todo-item ${todo.completed ? 'completed' : ''}`;
        todoItem.innerHTML = `
            <div class="todo-content">
                <span class="todo-text">${todo.title}</span>
                <span class="todo-time"><i class="far fa-clock"></i> ${todo.created_at}</span>
            </div>
            <div class="todo-actions">
                <button class="toggle" onclick="toggleTodo(${todo.id})">
                    <i class="fas ${todo.completed ? 'fa-undo' : 'fa-check'}"></i>
                    ${todo.completed ? 'Undo' : 'Complete'}
                </button>
                <button class="delete" onclick="deleteTodo(${todo.id})">
                    <i class="fas fa-trash"></i>
                    Delete
                </button>
            </div>
        `;
        todoList.appendChild(todoItem);
    });
}

// Add new todo
async function addTodo() {
    const input = document.getElementById('todoInput');
    const title = input.value.trim();
    if (!title) return;

    try {
        const response = await fetch('/api/todos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title }),
        });

        if (response.ok) {
            input.value = '';
            fetchTodos();
        } else {
            const errorData = await response.json();
            console.error('Failed to add todo:', errorData);
            alert('Failed to add todo: ' + (errorData.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error adding todo:', error);
        alert('Failed to add todo. Please try again.');
    }
}

// Delete todo
async function deleteTodo(id) {
    try {
        const response = await fetch(`/api/todos/${id}`, { method: 'DELETE' });
        if (response.ok) fetchTodos();
    } catch (error) {
        console.error('Error deleting todo:', error);
    }
}

// Toggle todo complete/incomplete
async function toggleTodo(id) {
    try {
        const response = await fetch(`/api/todos/${id}`, { method: 'PUT' });
        if (response.ok) fetchTodos();
    } catch (error) {
        console.error('Error toggling todo:', error);
    }
}
