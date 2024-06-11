function showForm() {
    document.getElementById('taskForm').style.display = 'block';
}

function hideForm() {
    document.getElementById('taskForm').style.display = 'none';
}

function addTask() {
    // Siin saate lisada koodi ülesande salvestamiseks
    alert('Ülesanne lisatud!');
    hideForm();
}