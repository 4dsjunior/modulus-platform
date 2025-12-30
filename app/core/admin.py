from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from supabase import create_client, Client
from app.utils import normalizar_texto
from app import supabase
import os

# Instância com Service Role (Super Admin) - Necessária para bypass de RLS e gestão de Auth
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
    
    # Verifica cache de sessão ou consulta banco para garantir privilégios
    if session.get('is_super_admin'):
        return None

    res = supabase.table("profiles").select("is_super_admin").eq("id", session['user_id']).single().execute()
    if res.data and res.data.get('is_super_admin'):
        session['is_super_admin'] = True # Otimização de performance
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
    Cria uma nova Unidade (Tenant) com normalização de texto.
    INTELIGÊNCIA: Se o e-mail já existe, vincula a nova unidade ao usuário existente.
    """
    if request.method == 'POST':
        # Captura e Normalização dos Dados
        raw_name = request.form.get('name')
        name = normalizar_texto(raw_name) # APLICAÇÃO DA NORMALIZAÇÃO (CAPS LOCK)
        
        slug = request.form.get('slug').lower().strip() # Slugs são sempre minúsculos por padrão de URL
        module_id = request.form.get('module_id')
        email = request.form.get('email').lower().strip() # Emails sempre em minúsculas
        password = request.form.get('password')

        tenant_id_created = None

        try:
            # 1. Tenta Criar a Nova Unidade (Tenant)
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
                auth_res = admin_supabase.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"full_name": name}
                })
                user_id = auth_res.user.id
                is_new_user = True
            
            except Exception as auth_error:
                # Caso o e-mail já exista, buscamos o ID no banco (Profiles)
                if "already been registered" in str(auth_error) or "email_exists" in str(auth_error):
                    print(f"Usuário {email} já existe. Tentando vincular...")
                    profile_res = admin_supabase.table("profiles").select("id").eq("email", email).single().execute()
                    if profile_res.data:
                        user_id = profile_res.data['id']
                    else:
                        raise Exception("E-mail existe no Auth mas o Perfil (Profile) não foi encontrado.")
                else:
                    raise auth_error

            # 3. Vincular Usuário à Nova Unidade como Proprietário (Owner)
            admin_supabase.table("tenant_members").insert({
                "tenant_id": tenant_id_created,
                "user_id": user_id,
                "role": "owner"
            }).execute()

            # 4. Ativar o Módulo Inicial selecionado
            admin_supabase.table("tenant_modules").insert({
                "tenant_id": tenant_id_created,
                "module_id": module_id,
                "is_enabled": True
            }).execute()

            # 5. Auditoria e Feedback
            msg_sucesso = f"Nova Unidade '{name}' criada! "
            msg_sucesso += "Novo usuário cadastrado." if is_new_user else "Vinculada ao usuário existente."

            log_action("CREATE_TENANT", {"slug": slug, "new_user": is_new_user}, target_user_id=user_id)
            flash(msg_sucesso)
            return redirect(url_for('admin.gerenciar_clientes'))

        except Exception as e:
            # ROLLBACK: Remove a unidade se a criação do vínculo falhar
            if tenant_id_created:
                admin_supabase.table("tenants").delete().eq("id", tenant_id_created).execute()
            
            flash(f"Falha ao criar unidade: {str(e)}")
            return redirect(url_for('admin.criar_cliente'))

    # GET: Carrega módulos disponíveis para o formulário
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

# --- ROTAS DE GESTÃO DE MÓDULOS POR CLIENTE ---

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
            flash("Módulo já existente para este cliente.")
        else:
            admin_supabase.table("tenant_modules").insert({"tenant_id": tenant_id, "module_id": module_id, "is_enabled": True}).execute()
            log_action("ADD_MODULE", {"tenant_id": tenant_id, "module_id": module_id})
            flash("Módulo adicionado com sucesso!")
    except Exception as e:
        flash(f"Erro: {str(e)}")
    return redirect(url_for('admin.gerenciar_modulos_cliente', tenant_id=tenant_id))

@admin_bp.route('/clientes/status_modulo/<tenant_id>/<module_id>/<int:novo_estado>', methods=['POST'])
def alterar_status_modulo(tenant_id, module_id, novo_estado):
    try:
        is_enabled = bool(novo_estado)
        admin_supabase.table("tenant_modules").update({"is_enabled": is_enabled}).eq("tenant_id", tenant_id).eq("module_id", module_id).execute()
        flash(f"Módulo {'ativado' if is_enabled else 'suspenso'} com sucesso.")
    except Exception as e:
        flash(f"Erro: {str(e)}")
    return redirect(url_for('admin.gerenciar_modulos_cliente', tenant_id=tenant_id))