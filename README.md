# Training-Manage

Este repositório contém o código-fonte de um sistema de gerenciamento de treinamento, dividido em duas aplicações Django independentes que se comunicam.

## Arquitetura do Projeto

O sistema é composto por dois projetos separados:

1.  **Backend (`/backend`)**
    * Construído com **Django REST Framework (DRF)**.
    * Atua como uma API RESTful, responsável por toda a lógica de negócios, gerenciamento de dados e autenticação.
    * Deve ser executado na porta `8000`.

2.  **Frontend (`/frontend`)**
    * Construído com **Django Templates** (renderização do lado do servidor).
    * Consome a API do `backend` para exibir e interagir com os dados.
    * Responsável pela interface do usuário.
    * Deve ser executado na porta `8001`.

## Requisitos

* Python 3.x
* Pip

## Instalação e Execução

Para rodar a aplicação corretamente, é **essencial** que os dois projetos (Backend e Frontend) estejam rodando simultaneamente em terminais separados.

---

### 1. Configuração do Backend (API)

Siga os passos abaixo para configurar e iniciar o servidor backend.

1.  Abra um terminal e navegue até o diretório `backend`:
    ```bash
    cd backend
    ```

2.  Crie um ambiente virtual (venv) para isolar as dependências:
    ```bash
    python -m venv venv
    ```

3.  Ative o ambiente virtual:
    * **No Windows (PowerShell/CMD):**
        ```bash
        .\venv\Scripts\activate
        ```
    * **No Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```

4.  Com o ambiente ativado, instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

5.  Aplique as migrações do banco de dados:
    ```bash
    python manage.py migrate
    ```

6.  Inicie o servidor backend na porta **8000**:
    ```bash
    python manage.py runserver 8000
    ```

**Deixe este terminal rodando.**

---

### 2. Configuração do Frontend (Templates)

Agora, configure o frontend em um **novo terminal**.

1.  Abra um **novo terminal** e navegue até o diretório `frontend` (a partir da raiz do projeto):
    ```bash
    cd frontend
    ```

2.  Crie um ambiente virtual (venv) separado para este projeto:
    ```bash
    python -m venv venv
    ```

3.  Ative o ambiente virtual:
    * **No Windows (PowerShell/CMD):**
        ```bash
        .\venv\Scripts\activate
        ```
    * **No Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```

4.  Com o ambiente ativado, instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

5.  Execute o `collectstatic` para coletar os arquivos estáticos (CSS, JS, imagens) do projeto:
    ```bash
    python manage.py collectstatic
    ```

6.  Inicie o servidor frontend na porta **8001**:
    ```bash
    python manage.py runserver 8001
    ```

**Deixe este segundo terminal rodando.**

## Acesso ao Sistema

Com os dois servidores rodando (backend na 8000 e frontend na 8001), acesse a aplicação frontend no seu navegador:

[http://localhost:8001](http://localhost:8001)

### Credenciais de Administrador

Utilize os seguintes dados para o login inicial:

* **Email:** `admin@gmail.com`
* **Senha:** `123456`
