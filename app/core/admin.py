from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app import supabase
import os
from supabase import create_client, Client

# Instância com Service Role (Super Admin)
admin_supabase: Client = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_SERVICE_KEY")
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- FUNÇÃO AUXILIAR DE AUDITORIA ---
def log_action(action, details, target_user_id=None):
    try:
        admin_supabase.table("audit_logs").insert({
            "performed_by": session.get('user_id'),
            "action": action,
            "target_user_id": target_user_id,
            "details": details
        }).execute()
    except Exception as e:
        print(f"ERRO DE AUDITORIA: {e}")

# --- MIDDLEWARE DE SEGURANÇA ---
@admin_bp.before_request
def restrict_to_superadmin():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Verifica cache de sessão ou consulta banco
    if session.get('is_super_admin'):
        return None

    res = supabase.table("profiles").select("is_super_admin").eq("id", session['user_id']).single().execute()
    if res.data and res.data.get('is_super_admin'):
        session['is_super_admin'] = True # Otimização
        return None
    
    flash("Acesso restrito ao Super Administrador.")
    return redirect(url_for('academia.dashboard'))

# --- ROTAS DE CLIENTES ---

@admin_bp.route('/clientes')
def gerenciar_clientes():
    """Lista todas as unidades (Tenants) cadastradas."""
    try:
        tenants = admin_supabase.table("tenants").select("*").order("name").execute()
        return render_template('admin/clientes.html', tenants=tenants.data if tenants.data else [])
    except Exception as e:
        flash(f"Erro ao carregar lista: {str(e)}")
        return render_template('admin/clientes.html', tenants=[])

@admin_bp.route('/clientes/novo', methods=['GET', 'POST'])
def criar_cliente():
    """
    Cria uma nova Unidade (Tenant).
    INTELIGÊNCIA: Se o e-mail já existe, vincula a nova unidade ao usuário existente.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        module_id = request.form.get('module_id')
        email = request.form.get('email')
        password = request.form.get('password')

        tenant_id_created = None

        try:
            # 1. Tenta Criar a Nova Unidade (Tenant)
            # O slug deve ser único (ex: titans-laranjeiras)
            tenant_res = admin_supabase.table("tenants").insert({
                "name": name,
                "slug": slug,
                "status": "active"
            }).execute()

            if not tenant_res.data:
                raise Exception("Erro ao criar a Unidade. Verifique se o Slug já existe.")
            
            tenant_id_created = tenant_res.data[0]['id']
            user_id = None
            is_new_user = False

            # 2. Gerenciar Usuário (Criação ou Busca)
            try:
                # Tenta criar usuário novo
                auth_res = admin_supabase.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"full_name": name} # Nome genérico inicial
                })
                user_id = auth_res.user.id
                is_new_user = True
            
            except Exception as auth_error:
                # Se der erro 422 (Email exists), buscamos o ID do usuário existente
                if "already been registered" in str(auth_error) or "email_exists" in str(auth_error):
                    # Como não temos "get_user_by_email" direto simples na lib padrão as vezes,
                    # fazemos uma query direta na tabela auth.users via service_role (Admin Power)
                    # Nota: Isso requer acesso ao schema auth, ou list_users
                    
                    # Tentativa via API Admin list_users (mais seguro)
                    # Pega o primeiro que bater o email
                    # Se falhar, lançamos o erro original
                    print(f"Usuário {email} já existe. Tentando vincular...")
                    
                    # Truque: Como não dá para filtrar por email no list_users facilmente em versoes antigas,
                    # podemos assumir que o admin sabe o que faz ou usar um RPC.
                    # Mas vamos tentar o método RPC seguro ou query direta se permitido.
                    
                    # Método Garantido (Service Role query na tabela de perfis que é espelho)
                    profile_res = admin_supabase.table("profiles").select("id").eq("email", email).single().execute()
                    if profile_res.data:
                        user_id = profile_res.data['id']
                        print(f"ID recuperado do perfil: {user_id}")
                    else:
                        raise Exception("E-mail existe no Auth mas não tem Perfil (Profile). Corrija o banco.")
                else:
                    raise auth_error

            # 3. Vincular Usuário à Nova Unidade (Owner)
            admin_supabase.table("tenant_members").insert({
                "tenant_id": tenant_id_created,
                "user_id": user_id,
                "role": "owner"
            }).execute()

            # 4. Ativar o Módulo Inicial
            admin_supabase.table("tenant_modules").insert({
                "tenant_id": tenant_id_created,
                "module_id": module_id,
                "is_enabled": True
            }).execute()

            # 5. Auditoria e Feedback
            msg_sucesso = f"Nova Unidade '{name}' criada! "
            if is_new_user:
                msg_sucesso += "Novo usuário cadastrado."
            else:
                msg_sucesso += "Vinculada ao usuário existente."

            log_action("CREATE_TENANT", {"slug": slug, "new_user": is_new_user}, target_user_id=user_id)
            flash(msg_sucesso)
            return redirect(url_for('admin.gerenciar_clientes'))

        except Exception as e:
            # ROLLBACK: Se falhar, apaga a unidade criada para não deixar lixo
            if tenant_id_created:
                admin_supabase.table("tenants").delete().eq("id", tenant_id_created).execute()
            
            flash(f"Falha ao criar unidade: {str(e)}")
            return redirect(url_for('admin.criar_cliente'))

    # GET
    modules_res = supabase.table("modules").select("*").execute()
    return render_template('admin/form_cliente.html', modules=modules_res.data)

@admin_bp.route('/clientes/status/<tenant_id>/<novo_status>', methods=['POST'])
def alterar_status(tenant_id, novo_status):
    try:
        admin_supabase.table("tenants").update({"status": novo_status}).eq("id", tenant_id).execute()
        log_action(f"CHANGE_STATUS_{novo_status.upper()}", {"tenant_id": tenant_id})
        flash(f"Status atualizado para {novo_status.upper()}.")
    except Exception as e:
        flash(f"Erro: {e}")
    return redirect(url_for('admin.gerenciar_clientes'))

# --- ROTAS DE MÓDULOS ---
@admin_bp.route('/clientes/modulos/<tenant_id>')
def gerenciar_modulos_cliente(tenant_id):
    try:
        modulos_cliente = admin_supabase.table("tenant_modules").select("module_id, is_enabled, modules(name)").eq("tenant_id", tenant_id).execute()
        todos_modulos = supabase.table("modules").select("*").execute()
        tenant = admin_supabase.table("tenants").select("name").eq("id", tenant_id).single().execute()
        
        return render_template('admin/modulos_cliente.html', 
                               modulos=modulos_cliente.data if modulos_cliente.data else [],
                               todos_modulos=todos_modulos.data,
                               tenant=tenant.data, tenant_id=tenant_id)
    except Exception as e:
        flash(f"Erro: {str(e)}")
        return redirect(url_for('admin.gerenciar_clientes'))

@admin_bp.route('/clientes/modulos/<tenant_id>/adicionar', methods=['POST'])
def adicionar_modulo(tenant_id):
    module_id = request.form.get('module_id')
    try:
        exists = admin_supabase.table("tenant_modules").select("*").eq("tenant_id", tenant_id).eq("module_id", module_id).execute()
        if exists.data:
            flash("Módulo já existente.")
        else:
            admin_supabase.table("tenant_modules").insert({"tenant_id": tenant_id, "module_id": module_id, "is_enabled": True}).execute()
            log_action("ADD_MODULE", {"tenant_id": tenant_id, "module_id": module_id})
            flash("Módulo adicionado!")
    except Exception as e:
        flash(f"Erro: {str(e)}")
    return redirect(url_for('admin.gerenciar_modulos_cliente', tenant_id=tenant_id))

@admin_bp.route('/clientes/status_modulo/<tenant_id>/<module_id>/<int:novo_estado>', methods=['POST'])
def alterar_status_modulo(tenant_id, module_id, novo_estado):
    try:
        is_enabled = bool(novo_estado)
        admin_supabase.table("tenant_modules").update({"is_enabled": is_enabled}).eq("tenant_id", tenant_id).eq("module_id", module_id).execute()
        flash(f"Módulo {'ativado' if is_enabled else 'suspenso'}.")
    except Exception as e:
        flash(f"Erro: {str(e)}")
    return redirect(url_for('admin.gerenciar_modulos_cliente', tenant_id=tenant_id))