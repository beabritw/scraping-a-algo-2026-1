   //Validação - Login
    const form        = document.getElementById('loginForm');
    const nameInput   = document.getElementById('userName');
    const emailInput  = document.getElementById('userEmail');
    const nameError   = document.getElementById('nameError');
    const emailError  = document.getElementById('emailError');
    const emailErrMsg = document.getElementById('emailErrorMsg');

    const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

    function setError(input, errorEl, msgEl, msg) {
        input.classList.add('invalid');
        input.setAttribute('aria-invalid', 'true');
        errorEl.classList.add('visible');
        if (msgEl) msgEl.textContent = msg;
    }

    function clearError(input, errorEl) {
        input.classList.remove('invalid');
        input.setAttribute('aria-invalid', 'false');
        errorEl.classList.remove('visible');
    }
    function validateName() {
        const val = nameInput.value.trim();
        if (!val) {
            setError(nameInput, nameError, null, '');
            return false;
        }
        clearError(nameInput, nameError);
        return true;
    }

    function validateEmail() {
        const val = emailInput.value.trim();
        if (!val) {
            setError(emailInput, emailError, emailErrMsg, 'Informe seu e-mail.');
            return false;
        }
        if (!EMAIL_REGEX.test(val)) {
            setError(emailInput, emailError, emailErrMsg, 'E-mail inválido — use o formato usuario@dominio.com');
            return false;
        }
        clearError(emailInput, emailError);
        return true;
    }

    nameInput.addEventListener('blur',  validateName);
    emailInput.addEventListener('blur', validateEmail);

    nameInput.addEventListener('input', () => {
        if (nameInput.classList.contains('invalid')) validateName();
    });

    emailInput.addEventListener('input', () => {
        if (emailInput.classList.contains('invalid')) validateEmail();
    });

    form.addEventListener('submit', (e) => {
        const nameOk  = validateName();
        const emailOk = validateEmail();

        if (!nameOk || !emailOk) {
            e.preventDefault();
            if (!nameOk)  nameInput.focus();
            else           emailInput.focus();
        }
    });