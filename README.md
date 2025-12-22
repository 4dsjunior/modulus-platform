# Modulus Platform 🚀

> **Status:** 🚧 Em Desenvolvimento (Alpha)
> **Módulo Atual:** Academia (Gestão Financeira Simplificada)

O **Modulus** é uma plataforma SaaS multi-tenant modular desenvolvida para resolver dores reais de pequenos empreendedores. A arquitetura foi desenhada para ser escalável, permitindo acoplar diferentes módulos (Academia, Nutrição, RH) sobre um mesmo Core de autenticação e segurança.

O foco inicial é o **Módulo Academia**, voltado para estúdios, personal trainers e pequenas academias que sofrem com gestão financeira manual (caderno/WhatsApp) e inadimplência por vergonha de cobrar.

---

## 🛠 Tech Stack & Arquitetura

O projeto preza pela **Estabilidade (LTS)** em vez de utilizar versões "bleeding edge" instáveis.

* **Linguagem:** Python **3.12+** (Estritamente. Python 3.13 não é suportado no momento).
* **Framework Web:** Flask 2.3.3 (Arquitetura Blueprints/Modular).
* **Banco de Dados:** Supabase (PostgreSQL) com RLS (Row Level Security).
* **Autenticação:** Supabase Auth (Integrado via Flask Session).
* **Frontend:** HTML5 + CSS3 (Jinja2 Templates).
* **Infraestrutura:** Gunicorn (WSGI).

### Estrutura de Pastas (Modular)
```text
/modulus-platform
├── app/
│   ├── core/           # O "Shopping Center" (Auth, Rotas Base)
│   ├── modules/        # As "Lojas" (Plugins independentes)
│   │   └── academia/   # Módulo de Gestão Financeira
│   ├── static/         # Assets globais
│   └── templates/      # HTMLs base
├── run.py              # Entry Point
└── requirements.txt    # Versões travadas (Locked)

Roadmap & Status
Fase 1: Fundação & Segurança (✅ Concluído)
[x] Definição de Arquitetura Modular (Flask Blueprints).

[x] Configuração do Ambiente Virtual Blindado (Python 3.12).

[x] Banco de Dados Supabase estruturado (Tenants, Profiles).

[x] Implementação de RLS (Row Level Security) no Banco.

[x] Sistema de Login Seguro (Integração Flask <-> Supabase).

[x] Blindagem de Sessão (Timeout de 30min, HttpOnly).

Fase 2: Módulo Academia - Core (🚧 Em Andamento)
[ ] Dashboard Inicial (Layout Base).

[ ] CRUD de Alunos (Listagem e Cadastro).

[ ] Motor de Matrículas (Vínculo Aluno <-> Plano).

[ ] Geração de Cobranças (Lógica de Snapshot Financeiro).

Fase 3: Funcionalidades de Negócio (Futuro)
[ ] Integração com WhatsApp (Link direto com mensagem pré-definida).

[ ] Geração de PIX (QR Code Dinâmico).

[ ] Relatórios Financeiros (Exportação Excel/Pandas).

[ ] Módulo "Modulus Nutri" (Expansão).

⚙️ Instalação e Configuração
1. Pré-requisitos
Python 3.12.x instalado (Verifique com py -3.12 --version).

Conta no Supabase configurada.

2. Clonar e Configurar Ambiente
Bash

git clone [https://github.com/4dsjunior/modulus-platform.git](https://github.com/4dsjunior/modulus-platform.git)
cd modulus-platform

# Criar ambiente virtual forçando Python 3.12 (Windows)
py -3.12 -m venv venv

# Ativar ambiente
.\venv\Scripts\Activate
3. Instalar Dependências
Bash

# Atualizar o pip para garantir resolução correta
python -m pip install --upgrade pip

# Instalar pacotes travados
pip install -r requirements.txt
4. Configurar Variáveis de Ambiente
Crie um arquivo .env na raiz e preencha:

Ini, TOML

SUPABASE_URL=sua_url_aqui
SUPABASE_KEY=sua_chave_anon_aqui
FLASK_SECRET_KEY=gere_uma_chave_segura_aqui
FLASK_ENV=development
5. Rodar
Bash

python run.py
🔧 Troubleshooting (Erros Conhecidos & Soluções)
Durante o desenvolvimento, enfrentamos conflitos severos de versão. Abaixo está o registro das soluções para evitar regressão.

🔴 Erro: metadata-generation-failed / Falha ao instalar Pandas
Sintoma: O pip install trava tentando compilar o Pandas/Numpy, exigindo Visual C++ ou Meson/Ninja.

Causa: O ambiente estava rodando Python 3.13. As bibliotecas de dados (Pandas, Numpy) ainda não possuem binários pré-compilados (wheels) para Windows no Python 3.13.

Solução: Downgrade obrigatório para Python 3.12. O projeto foi travado nesta versão.

🔴 Erro: TypeError: Client.__init__() got an unexpected keyword argument 'proxy'
Sintoma: O sistema quebrava ao tentar conectar no Supabase.

Causa: A biblioteca httpx atualizou para a versão 0.28.0+, alterando a assinatura de conexão. O cliente do Supabase (supabase-py) ainda esperava a versão antiga.

Solução: Travamos a versão do httpx no requirements.txt:

Plaintext

httpx==0.27.2
🔴 Erro: Conflicting dependencies: storage3
Sintoma: O pip recusava instalar os pacotes, alegando conflito entre supabase e storage3.

Causa: Tentamos forçar versões manuais de sub-dependências (storage3==0.7.2) que não eram compatíveis com a versão pai (supabase==2.9.1).

Solução: Removemos as sub-dependências do requirements.txt e deixamos apenas o pacote pai (supabase) gerenciar o que ele precisa instalar.

🔴 Erro: Fatal error in launcher
Sintoma: Ao rodar pip install, o terminal retornava erro fatal.

Causa: Lixo de instalações anteriores ou caminhos de Python corrompidos no Windows.

Solução:

Usar python -m pip em vez de apenas pip.

Recriar o venv do zero.

🤝 Contribuição
Garanta que está usando Python 3.12.

Não atualize bibliotecas via pip install --upgrade sem testar a matriz de compatibilidade do Supabase.


---

### Próximo Passo Sugerido no Github:
Depois de salvar esse arquivo, execute os comandos no terminal do VS Code para subir para o repositório:

```powershell
git add .
git commit -m "Docs: Adiciona README com roadmap e troubleshooting de versoes"
git branch -M main
git remote add origin https://github.com/4dsjunior/modulus-platform.git
# (Se der erro que a origem já existe, ignore essa linha acima)
git push -u origin main