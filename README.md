# Scraping - Assistente de Lances

Guia rápido para rodar o projeto.

## Clonar Repositório
```bash
git clone https://github.com/beabritw/scraping-a-algo-2026-1.git

cd scraping-a-algo-2026-1
```


## Preparar Ambiente
No terminal, na raiz do projeto, execute:
```bash
python3 -m venv .venv

# Ou venv\Scripts\activate se for no windows
source .venv/bin/activate

# Instala dependencias do projeto
pip install -r requirements.txt 

```


## Crie um .env com o conteudo:

Para que o notificador consiga disparar os alertas via Gmail, o Google exige uma Senha de App. Não utilize sua senha padrão.

Na raiz do projeto, crie um arquivo chamado .env.
Adicione a sua senha de 16 caracteres gerada pelo Google no seguinte formato:

```bash
EMAIL_SENHA=abcdefghijklmnop
```


## Execute no terminal:

```bash
python orquestrador.py
```

---

#### Exemplo do recebimemto do email com valor antigo e atualizado:
<img width="1033" height="490" alt="image" src="https://github.com/user-attachments/assets/a1ec37f5-ce4b-45ee-9620-cc4823d2ee31" />

---

## Desenvolvedores:
- Beatriz Brito
- Davi de Souza
- Giovanna Monteiro
- Leonardo Dias
- Mariana Paiva
- Othon Flávio
