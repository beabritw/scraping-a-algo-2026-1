document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('btnContinuar');
    const inputNome = document.getElementById('userName');
    const inputEmail = document.getElementById('userEmail');
    const displayErro = document.getElementById('mensagemErro');

    // Função para validar formato básico de e-mail
    const validarEmail = (email) => {
        return email.includes('@') && email.includes('.');
    };

    btn.addEventListener('click', () => {
        const nome = inputNome.value.trim();
        const email = inputEmail.value.trim();
        const proximaRota = btn.getAttribute('data-url');

        // Limpa a mensagem de erro anterior
        displayErro.textContent = "";

        // Validação de campos vazios
        if (nome !== "" && email !== "") {
            
            // Validação de formato de e-mail
            if (!validarEmail(email)) {
                displayErro.textContent = "Por favor, insira um e-mail válido.";
                return;
            }

            localStorage.setItem('userName', nome);
            localStorage.setItem('userEmail', email);

            // Agora sim, redireciona para a Tela 2
            window.location.href = proximaRota;
            
        } else {
            // Feedback visual em caso de campos vazios
            displayErro.textContent = "Insira os dados para continuar";
        }
    });
});
