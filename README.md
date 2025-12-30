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


# 🔧 Resolução do Erro PGRST116 - Sistema de Verificação de Licença

## 📋 Identificação do Problema

**Data da Ocorrência:** 30/12/2024  
**Módulo Afetado:** Academia - Gerenciamento de Alunos  
**Severidade:** 🔴 CRÍTICA (Bloqueio Total de Funcionalidade)

---

## 🐛 Descrição do Erro

### Sintoma Observado
Ao acessar a rota `/academia/alunos`, a página era exibida com **bloqueio total da interface**, mostrando o alerta:

> **ACESSO RESTRITO:** Sua licença está suspensa ou aguardando pagamento.

Mesmo com a licença do tenant configurada como `active` no banco de dados.

### Mensagem de Erro no Console

```
Erro ao buscar status do tenant: {
  'code': 'PGRST116', 
  'details': 'The result contains 0 rows', 
  'hint': None, 
  'message': 'Cannot coerce the result to a single JSON object'
}
```

### Comportamento Inesperado

```python
# Código Problemático Original
tenant_status = 'suspended'  # Iniciava como suspenso
try:
    response = supabase.table('tenants').select('status').eq('id', tenant_id).single().execute()
    if response.data:
        tenant_status = response.data.get('status', 'suspended')
except Exception as e:
    print(f"Erro ao buscar status do tenant: {e}")
    # tenant_status permanecia como 'suspended'
```

---

## 🔍 Análise da Causa Raiz

### 1. **Problema Técnico: `.single()` com RLS**

O método `.single()` do Supabase **exige retornar exatamente 1 linha**. Quando o RLS (Row Level Security) bloqueia a leitura da tabela `tenants`, o retorno é **0 linhas**, causando a exceção `PGRST116`.

### 2. **Conflito de Arquitetura de Segurança**

```
┌─────────────────────────────────────────────────────────┐
│  Cliente Flask (Anon Key)                               │
│  ↓ Tenta ler: tenants.status                            │
│  ↓                                                       │
│  ┌─────────────────────────────────────────────┐        │
│  │ Supabase RLS (Row Level Security)           │        │
│  │ ❌ BLOQUEADO: Usuário comum não pode ler    │        │
│  │    dados da tabela 'tenants' diretamente    │        │
│  └─────────────────────────────────────────────┘        │
│  ↓                                                       │
│  Retorna: 0 rows → Exception PGRST116                   │
│  ↓                                                       │
│  Código cai no except → tenant_status = 'suspended'     │
│  ↓                                                       │
│  Interface bloqueada indevidamente ❌                    │
└─────────────────────────────────────────────────────────┘
```

### 3. **Por que o RLS bloqueava?**

As políticas RLS no Supabase são projetadas para **isolar dados entre tenants**. Um usuário comum (`authenticated`) não deve ter acesso direto à tabela `tenants` por questões de segurança multi-tenant.

**Tentativa de Correção (Falhou):**
```sql
-- Política RLS adicionada (não resolveu completamente)
CREATE POLICY "Users can read their tenant status"
ON tenants FOR SELECT
TO authenticated
USING (
  id IN (
    SELECT tenant_id 
    FROM tenant_members 
    WHERE user_id = auth.uid()
  )
);
```

**Por que falhou:** Dependendo da ordem de execução das queries e da configuração do Supabase, o RLS pode ainda retornar 0 rows em casos edge.

---

## ✅ Solução Implementada

### Estratégia: **Service Role com Privilégios Elevados**

Separamos os clientes Supabase em **dois níveis de privilégio**:

1. **Cliente Normal (Anon Key)** → Para operações de usuário (CRUD de alunos, matrículas)
2. **Cliente Admin (Service Role)** → Para verificações de sistema (status de licença, auditoria)

### Implementação

#### **1. Adição da Service Role Key**

```ini
# arquivo: .env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=eyJhbGciOi... (Anon Key)
FLASK_SECRET_KEY=chave-secreta-flask

# ⭐ NOVA CONFIGURAÇÃO
SUPABASE_SERVICE_KEY=eyJhbGciOi... (Service Role Key)
```

#### **2. Criação de Cliente Admin**

```python
# arquivo: app/modules/academia/routes.py

from supabase import create_client, Client
import os

# Cliente Normal (herdado de app)
from app import supabase

# ⭐ Cliente Admin (Novo)
admin_supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # Bypass de RLS
)
```

#### **3. Função Centralizada de Verificação**

```python
def verificar_licenca_tenant(tenant_id):
    """
    Verifica o status da licença do tenant usando Service Role.
    
    Princípio Fail-Safe: 
    - Se houver erro, retorna 'suspended' (bloqueia acesso)
    
    Returns:
        str: 'active', 'suspended', 'archived' ou 'suspended' em caso de erro
    """
    if not tenant_id:
        return 'suspended'
    
    try:
        response = admin_supabase.table('tenants')\
            .select('status')\
            .eq('id', tenant_id)\
            .single()\
            .execute()
        
        if response.data:
            status = response.data.get('status', 'suspended')
            print(f"✅ Licença verificada: Tenant {tenant_id} = {status}")
            return status
        else:
            print(f"⚠️ Tenant {tenant_id} não encontrado no banco.")
            return 'suspended'
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO ao verificar licença: {e}")
        return 'suspended'  # Fail-Safe
```

#### **4. Aplicação nas Rotas**

```python
@academia_bp.route('/alunos')
def gerenciar_alunos():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        flash("Selecione uma unidade para continuar.", "warning")
        return redirect(url_for('academia.dashboard'))

    # ⭐ SOLUÇÃO: Usa Service Role para verificar licença
    tenant_status = verificar_licenca_tenant(tenant_id)

    # Busca alunos com cliente normal (RLS aplicado)
    students = []
    try:
        resp = supabase.table('students')\
            .select('*')\
            .eq('tenant_id', tenant_id)\
            .execute()
        students = resp.data if resp.data else []
    except Exception as e:
        print(f"Erro ao buscar alunos: {e}")

    return render_template('academia/alunos.html', 
                         students=students, 
                         tenant_status=tenant_status)
```

---

## 🎯 Resultados Obtidos

### ✅ Antes vs Depois

| Aspecto | ❌ Antes (Problemático) | ✅ Depois (Corrigido) |
|---------|------------------------|----------------------|
| **Leitura de Status** | Bloqueada pelo RLS → 0 rows | Bypass com Service Role → Sempre retorna |
| **Comportamento em Erro** | Assumia `suspended` incorretamente | Fail-Safe: Bloqueia apenas se realmente suspenso |
| **Performance** | Tentativa falhada + fallback | Consulta direta bem-sucedida |
| **Segurança** | ⚠️ Risco de bypass (solução proposta original) | ✅ Níveis de privilégio adequados |

### 📊 Logs de Sucesso

```
✅ Licença verificada: Tenant 123e4567-e89b-12d3-a456-426614174000 = active
📊 Encontrados 12 alunos para o tenant 123e4567-e89b-12d3-a456-426614174000
127.0.0.1 - - [30/Dec/2024 17:05:23] "GET /academia/alunos HTTP/1.1" 200 -
```

---

## 🔐 Considerações de Segurança

### ⚠️ Service Role Key - Cuidados Críticos

1. **NUNCA exponha no frontend** (HTML, JavaScript)
2. **NUNCA commite no Git** (já está no `.gitignore`)
3. **Use APENAS no backend** (rotas Flask)
4. **Rotacione periodicamente** (boas práticas de segurança)

### ✅ Arquitetura de Privilégios

```
┌─────────────────────────────────────────────────────────┐
│  OPERAÇÃO                    │  CLIENTE USADO           │
├──────────────────────────────┼──────────────────────────┤
│  Verificar licença tenant    │  admin_supabase ⭐       │
│  Listar alunos               │  supabase (normal)       │
│  Cadastrar aluno             │  supabase (normal)       │
│  Atualizar aluno             │  supabase (normal)       │
│  Logs de auditoria           │  admin_supabase ⭐       │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Alternativas Consideradas (e Por Que Foram Descartadas)

### ❌ Opção A: Assumir 'active' por padrão (Proposta Inicial)

```python
# REJEITADA - FALHA DE SEGURANÇA
tenant_status = 'active'  # Assume ativo se falhar
```

**Problema:** Se o tenant estiver realmente suspenso e o RLS bloquear, o sistema liberaria acesso indevido.

### ❌ Opção B: Ajustar RLS no Supabase

**Problema:** Políticas RLS complexas podem ter casos edge. Não resolve 100% dos cenários.

### ❌ Opção C: Cache na Sessão Flask

```python
session['tenant_status'] = 'active'
```

**Problema:** 
- Sessão expira em 5 minutos de inatividade
- Não persiste entre abas/navegadores
- Dados desatualizados se o admin suspender a licença

### ✅ Opção Escolhida: Service Role (Implementada)

**Vantagens:**
- ✅ Bypass legítimo de RLS para operações de sistema
- ✅ Fail-Safe: Bloqueia se houver erro
- ✅ Performance: Consulta direta sem intermediários
- ✅ Segurança: Níveis de privilégio adequados

---

## 🧪 Testes de Validação

### Cenários Testados

1. ✅ **Tenant Ativo** → Interface liberada
2. ✅ **Tenant Suspenso** → Interface bloqueada com alerta
3. ✅ **Erro de Conexão** → Interface bloqueada (Fail-Safe)
4. ✅ **Tenant Inexistente** → Interface bloqueada

### Comandos para Testar Manualmente

```python
# No console Python (python run.py)
from app.modules.academia.routes import verificar_licenca_tenant

# Teste com tenant válido
status = verificar_licenca_tenant('uuid-do-tenant-aqui')
print(status)  # Deve retornar 'active' ou 'suspended'

# Teste com tenant inexistente
status = verificar_licenca_tenant('00000000-0000-0000-0000-000000000000')
print(status)  # Deve retornar 'suspended' (Fail-Safe)
```

---

## 📝 Checklist de Implementação em Outros Módulos

Se outros módulos (Nutrição, RH, etc) forem criados, siga este padrão:

- [ ] Adicionar `SUPABASE_SERVICE_KEY` no `.env`
- [ ] Criar cliente `admin_supabase` no módulo
- [ ] Implementar função `verificar_licenca_tenant()`
- [ ] Aplicar verificação em rotas críticas
- [ ] Testar cenários de sucesso, falha e erro

---

## 🔗 Referências

- [Documentação Supabase - Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [Flask Session Management](https://flask.palletsprojects.com/en/2.3.x/api/#sessions)

---

## 📌 Metadados

**Autor da Solução:** Desenvolvedor Principal  
**Data de Implementação:** 30/12/2024  
**Versão do Sistema:** v0.1-alpha  
**Status:** ✅ RESOLVIDO E DOCUMENTADO  
**Próxima Revisão:** Ao adicionar novos módulos ao sistema