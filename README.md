# Lynx Monitor — Assistente de Lances

> Ferramenta de alta performance para monitoramento de alterações em páginas web com notificações automáticas via e-mail.

O **Lynx Monitor** rastreia variações de preços ou conteúdos específicos em qualquer página web e dispara alertas automáticos no momento em que uma mudança é detectada. Construído com arquitetura modular que separa a interface de usuário do motor de busca e monitoramento.

---


## Como Executar

### Clonar o repositório

```bash
git clone https://github.com/beabritw/scraping-a-algo-2026-1.git
cd scraping-a-algo-2026-1
```

### Configurar credenciais

Crie um arquivo `.env` na raiz do projeto com sua [Senha de App do Google](https://myaccount.google.com/apppasswords) (16 caracteres):

```
EMAIL_SENHA=sua_senha_de_16_digitos_aqui
FLASK_SECRET_KEY=sua_chave_secreta_aqui
```

> **Como gerar a senha de app:** acesse `myaccount.google.com` → Segurança → Verificação em duas etapas (ativar) → Senhas de app → criar nova.

> **Como gerar a secret key do Flask:**
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### Executar com o assistente de inicialização

O script `iniciar.sh` cria o ambiente virtual, instala dependências, roda os testes e sobe os servidores automaticamente.

```bash
# Conceda permissão de execução (apenas na primeira vez)
chmod +x iniciar.sh

# Inicie o assistente
./iniciar.sh
```

---

Ao rodar `./iniciar.sh`, um menu interativo oferece as seguintes opções:

| Opção | Descrição |
|-------|-----------|
| `1` Terminal (CLI) | Executa `orquestrador.py` — interface de linha de comando completa |
| `2` Interface Web | Inicia o servidor Flask na porta `http://localhost:5000` |
| `3` Documentação | Sobe o portal MkDocs na porta `http://localhost:8000` |
| `4` Modo Apresentação | Inicia a Interface Web e a Documentação simultaneamente |

### Execução manual (sem o script)

```bash
# Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

# Instalar dependências
pip install -r requirements.txt

# CLI
python orquestrador.py

# Interface web
python interface/app.py

# Testes
pytest -v
```
---

## Análise de Complexidade

O motor de monitoramento utiliza `lxml` com processamento em árvore DOM.

| Operação | Complexidade | Descrição |
|----------|-------------|-----------|
| `carregar_pagina()` | O(1) | Chamada ao driver, sem percorrer estruturas locais |
| `localizar_elemento()` | O(n) | Percorre o DOM — n = nós na página |
| `_obter_xpath()` | O(d) | Sobe a árvore até a raiz — d = profundidade do elemento |
| Iteração do monitoramento | O(n) | Recarrega e relocaliza por iteração |
| **Total do monitoramento** | **O(k·n)** | k = número de iterações |
| Memória (histórico) | O(a) | a = número de alterações detectadas |

Para análise matemática detalhada, consulte [`big_o.md`](./big_o.md) ou acesse a documentação via opção `3` do script de inicialização.

---

## Notificações por E-mail

#### Exemplo do recebimemto do email com valor antigo e atualizado:

<img width="1033" height="490" alt="image" src="https://github.com/user-attachments/assets/a1ec37f5-ce4b-45ee-9620-cc4823d2ee31" />
---

Quando uma alteração é detectada, o sistema dispara automaticamente um alerta para o e-mail cadastrado pelo usuário com o valor anterior e o valor atual.

O remetente fixo é `assistentedelances@gmail.com`. O envio utiliza o protocolo SMTP com TLS via `smtplib` (biblioteca padrão do Python — sem dependência externa).

---

## Desenvolvedores:
- Beatriz Brito
- Davi de Souza
- Giovanna Monteiro
- Leonardo Dias
- Mariana Paiva
- Othon Flávio

Projeto desenvolvido para a disciplina de Análise de Algoritmos — IESB · Ciência da Computação · 2026/1

---
*© 2026 Lynx Monitor Project · IESB · Ciência da Computação*
