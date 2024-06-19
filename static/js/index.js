function showRegister() {
    document.getElementById('register-overlay').style.display = 'flex';
    document.querySelector('body').classList.add('blur');
}

function hideRegister() {
    document.getElementById('register-overlay').style.display = 'none';
    document.querySelector('body').classList.remove('blur');
}

function showLogin() {
    document.getElementById('login-overlay').style.display = 'flex';
    document.querySelector('body').classList.add('blur');
}

function hideLogin() {
    document.getElementById('login-overlay').style.display = 'none';
    document.querySelector('body').classList.remove('blur');
}
function showErrorMessage() {
    var errorMessage = document.getElementById('error-message');
    errorMessage.style.display = 'block'; // Kuvame veateate
}

function hideErrorMessage() {
    var errorMessage = document.getElementById('error-message');
    errorMessage.style.display = 'none'; // Peidame veateate
}
document.getElementById('login_username').addEventListener('input', hideErrorMessage);
document.getElementById('login_password').addEventListener('input', hideErrorMessage);

