# RAG Assistant (LGPD Compliant) 🛡️🤖

Este projeto é um **Assistente RAG (Retrieval-Augmented Generation)** construído com uma arquitetura moderna e segura, com foco estrito na compliance com a **LGPD (Lei Geral de Proteção de Dados)**.

O sistema permite que você carregue documentos privados (como políticas da empresa, atas ou PDFs gerais), transforme-os em conhecimento matemático (embeddings) e construa um chat inteligente capaz de tirar dúvidas consultando, de maneira segura, exclusivamente a sua base local de arquivos.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![NextJS](https://img.shields.io/badge/Next.js-16+-black)
![Postgres](https://img.shields.io/badge/PostgreSQL-pgvector-blue)

## 🚀 Principais Features

- **Sanitização de PII (LGPD):** Todo documento enviado passa por um Guardrail com Regex e LLM para ocultar nomes, endereços, e-mails e aplicar máscaras automáticas em CPFs *antes* do salvamento no banco de dados.
- **RAG com Busca Semântica:** Utiliza bancos vetoriais (`pgvector`) aliando a distância por cosseno à potência dos Embeddings do modelo Gemini do Google.
- **Query Refiner:** As perguntas do usuário são otimizadas via IA antes da busca no banco de dados para garantir altíssima precisão no contexto recuperado.
- **Ingestão em Lote:** Scripts Node.js auxiliares para ler dezenas de TXTs e PDFs e enviá-los para a vetorização.
- **Model Context Protocol (MCP):** Acompanha um servidor MCP isolado demonstrando como expor leitura de arquivos nativos do SO para agentes externos de IA.

## 🛠️ Stack Tecnológica

**Back-End:**
*   [Python 3](https://www.python.org/)
*   [FastAPI](https://fastapi.tiangolo.com/) (APIs rápidas e assíncronas)
*   [SQLAlchemy](https://www.sqlalchemy.org/) + [pgvector](https://github.com/pgvector/pgvector-python)
*   [Google GenAI SDK](https://ai.google.dev/) (Integração oficial do Gemini 2.5)

**Front-End:**
*   [Next.js 16](https://nextjs.org/) (React)
*   CSS Modular

**Infraestrutura:**
*   [Docker Compose](https://docs.docker.com/compose/)
*   PostgreSQL com extensão PGVector

---

## ⚙️ Como rodar o projeto localmente

### 1. Pré-requisitos
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) rodando ativamente.
*   [Python 3.10+](https://www.python.org/downloads/) instalado.
*   [Node.js (LTS)](https://nodejs.org/) instalado.
*   Uma chave válida da API do Google Gemini.

### 2. Configurando o Banco de Dados
A partir da raiz do projeto, suba o container do Postgres contendo a extensão vetorial:
```bash
docker compose up -d
```

### 3. Configurando o Back-End (Python)
Abra a pasta do backend:
```bash
cd backend
```
Crie seu ambiente virtual, ative-o e instale os pacotes:
```bash
python -m venv venv
# No Windows PowerShell:
.\venv\Scripts\Activate.ps1
# No Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```
Agora crie um arquivo `.env` na pasta `backend` com a sua chave de API:
```env
GEMINI_API_KEY=sua_chave_aqui
```
Crie as tabelas do banco de dados e inicie a API:
```bash
cd app
python init_db.py
cd ..
uvicorn app.main:app --reload --port 8000
```

### 4. Configurando o Front-End (React/Next.js)
Abra outro terminal na pasta `frontend`:
```bash
cd frontend
npm install
npm run dev
```
Basta acessar [http://localhost:3000](http://localhost:3000) no seu navegador!
