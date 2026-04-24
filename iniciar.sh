#!/bin/bash

echo "=========================================="
echo "  Lynx Monitor - Script de Inicialização  "
echo "=========================================="

echo "🧹 Limpando portas e processos antigos..."
fuser -k 5000/tcp 2>/dev/null
fuser -k 8000/tcp 2>/dev/null
sleep 1

if [ ! -f .env ]; then
    echo "Aviso: Arquivo .env não encontrado!"
    read -p "Digite a sua EMAIL_SENHA (16 caracteres do Google) para criarmos o arquivo agora: " email_senha
    echo "EMAIL_SENHA=$email_senha" > .env
    echo "Arquivo .env criado com sucesso."
else
    echo "Arquivo .env já configurado."
fi

if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual isolado (.venv)..."
    python3 -m venv .venv
fi

echo "Ativando ambiente virtual..."
source .venv/bin/activate

echo "Instalando/Atualizando dependências..."
pip install -r requirements.txt -q
echo "Dependências prontas."
echo "------------------------------------------"

echo "Executando suíte de testes (Pytest)..."
pytest -v

if [ $? -ne 0 ]; then
    echo "------------------------------------------"
    echo "ALERTA: Os testes falharam!"
    echo "Corrija os erros listados acima antes de iniciar o sistema."
    exit 1
fi
echo "Todos os testes passaram! Código seguro."
echo "------------------------------------------"

echo "Tudo pronto! Escolha o próximo passo:"
echo "1) Terminal (Orquestrador - CLI)"
echo "2) Interface Web (Flask - app.py)"
echo "3) Documentação (MkDocs)"
echo "4) Rodar Web e Docs JUNTOS (Processos em Paralelo)"
echo "5) Sair"
read -p "Escolha uma opção (1-5): " opcao

case $opcao in
    1)
        echo "Iniciando Orquestrador..."
        python orquestrador.py
        ;;
    2)
        echo "Iniciando Interface Web (http://127.0.0.1:5000)..."
        python interface/app.py
        ;;
    3)
        echo "Iniciando Documentação (http://127.0.0.1:8000)..."
        mkdocs serve
        ;;
    4)
        echo "Iniciando Documentação e Interface Web..."
        echo "Acesse o site em http://127.0.0.1:5000 e os docs em http://127.0.0.1:8000"
        echo "Pressione CTRL+C a qualquer momento para desligar ambos."
        
        trap 'kill $(jobs -p) 2>/dev/null; echo -e "\n🛑 Processos encerrados."; exit' SIGINT SIGTERM

        mkdocs serve &
        python interface/app.py &
        
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