document.querySelectorAll('.deleteCheckbox').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        if (this.checked) {
            this.closest('.deleteForm').submit();
        }
    });
});

function showForm() {
    document.getElementById('taskForm').style.display = 'block';
    document.querySelector('.container').classList.add('blur');
}

function hideForm() {
    document.getElementById('taskForm').style.display = 'none';
    document.querySelector('.container').classList.remove('blur');
}

function showEdit(button) {
    const taskItem = button.closest('.todo-item');
    const taskId = taskItem.getAttribute('data-id');
    const taskTitle = taskItem.getAttribute('data-title');
    const taskBody = taskItem.getAttribute('data-body');

    document.getElementById('editTaskId').value = taskId;
    document.getElementById('taskTitleEdit').value = taskTitle;
    document.getElementById('taskBodyEdit').value = taskBody;

    document.getElementById('taskEdit').style.display = 'block';
    document.querySelector('.container').classList.add('blur');
}

function hideEdit() {
    document.getElementById('taskEdit').style.display = 'none';
    document.querySelector('.container').classList.remove('blur');
}

function addTask() {
    // Siin saate lisada koodi ülesande salvestamiseks
    alert('Ülesanne lisatud!');
    hideForm();
}
