#!/bin/bash

echo "=========================================="
echo "  Lynx Monitor - Script de Inicialização  "
echo "=========================================="

# 1. Verificação de Segurança do .env
if [ ! -f .env ]; then
    echo "⚠️  Aviso: Arquivo .env não encontrado!"
    read -p "Digite a sua EMAIL_SENHA (16 caracteres do Google) para criarmos o arquivo agora: " email_senha
    echo "EMAIL_SENHA=$email_senha" > .env
    echo "✅ Arquivo .env criado com sucesso."
else
    echo "✅ Arquivo .env já configurado."
fi

# 2. Configuração do Ambiente Virtual
if [ ! -d ".venv" ]; then
    echo "⚙️  Criando ambiente virtual isolado (.venv)..."
    python3 -m venv .venv
fi

echo "🔌 Ativando ambiente virtual..."
source .venv/bin/activate

echo "📦 Instalando/Atualizando dependências..."
pip install -r requirements.txt -q
echo "✅ Dependências prontas."
echo "------------------------------------------"

# 3. Auditoria de Código (Testes Unitários)
echo "🧪 Executando suíte de testes (Pytest)..."
pytest -v

# Captura o código de saída do pytest. Se for diferente de 0, algo falhou.
if [ $? -ne 0 ]; then
    echo "------------------------------------------"
    echo "❌ ALERTA: Os testes falharam!"
    echo "Corrija os erros listados acima antes de iniciar o sistema."
    exit 1
fi
echo "✅ Todos os testes passaram! Código seguro."
echo "------------------------------------------"

# 4. Roteamento de Execução
echo "Tudo pronto, equipe! O que vocês desejam apresentar agora?"
echo "1) Terminal (Orquestrador - CLI)"
echo "2) Interface Web (Flask - app.py)"
echo "3) Documentação (MkDocs)"
echo "4) Rodar Web e Docs JUNTOS (Processos em Paralelo)"
echo "5) Sair"
read -p "Escolha uma opção (1-5): " opcao

case $opcao in
    1)
        echo "🚀 Iniciando Orquestrador..."
        python orquestrador.py
        ;;
    2)
        echo "🚀 Iniciando Interface Web (http://127.0.0.1:5000)..."
        python interface/app.py
        ;;
    3)
        echo "🚀 Iniciando Documentação (http://127.0.0.1:8000)..."
        mkdocs serve
        ;;
    4)
        echo "🚀 Iniciando Documentação e Interface Web..."
        echo "Acesse o site em http://127.0.0.1:5000 e os docs em http://127.0.0.1:8000"
        echo "Pressione CTRL+C a qualquer momento para desligar ambos."
        
        # O operador '&' joga o processo para o background
        mkdocs serve &
        python interface/app.py &
        
        # O comando 'wait' segura o terminal aberto até você pressionar CTRL+C
        wait 
        ;;
    5)
        echo "Encerrando."
        exit 0
        ;;
    *)
        echo "Opção inválida. Execute o script novamente."
        exit 1
        ;;
esac