from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app import supabase
import os
from supabase import create_client

# Instância com Service Role para ignorar RLS e realizar operações de Admin
admin_supabase = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_SERVICE_KEY")
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def restrict_to_superadmin():
    """Garante que apenas o Super Admin acesse este módulo."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Verifica se o perfil do usuário logado é super admin
    res = supabase.table("profiles").select("is_super_admin").eq("id", session['user_id']).single().execute()
    
    if not res.data or not res.data.get('is_super_admin'):
        flash("Acesso restrito ao Super Administrador.")
        return redirect(url_for('academia.dashboard'))

@admin_bp.route('/clientes')
def gerenciar_clientes():
    """Lista todos os clientes (Tenants) usando a chave de serviço para ignorar RLS."""
    try:
        # Usamos admin_supabase para garantir que o Super Admin veja TUDO
        tenants = admin_supabase.table("tenants").select("*").order("name").execute()
        return render_template('admin/clientes.html', tenants=tenants.data if tenants.data else [])
    except Exception as e:
        flash(f"Erro ao carregar clientes: {str(e)}")
        return render_template('admin/clientes.html', tenants=[])

@admin_bp.route('/clientes/novo', methods=['GET', 'POST'])
def criar_cliente():
    """Busca módulos e processa a criação de um novo cliente SaaS."""
    
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        module_id = request.form.get('module_id')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # 1. Criar o Tenant (A empresa/academia)
            tenant_res = admin_supabase.table("tenants").insert({
                "name": name,
                "slug": slug,
                "status": "active"
            }).execute()

            if not tenant_res.data:
                raise Exception("Erro ao criar registro do Tenant.")
            
            tenant_id = tenant_res.data[0]['id']

            # 2. Criar o Usuário no Auth do Supabase (Login direto com email confirmado)
            auth_res = admin_supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"full_name": name}
            })

            if not auth_res.user:
                raise Exception("Erro ao criar usuário de autenticação.")

            user_id = auth_res.user.id

            # 3. Vincular Usuário ao Tenant como 'owner'
            admin_supabase.table("tenant_members").insert({
                "tenant_id": tenant_id,
                "user_id": user_id,
                "role": "owner"
            }).execute()

            # 4. Ativar o Módulo escolhido para este Tenant
            admin_supabase.table("tenant_modules").insert({
                "tenant_id": tenant_id,
                "module_id": module_id,
                "is_enabled": True
            }).execute()

            flash(f"Sucesso! Academia '{name}' criada e módulo '{module_id}' ativado.")
            return redirect(url_for('admin.gerenciar_clientes'))

        except Exception as e:
            flash(f"Falha na operação: {str(e)}")
            return redirect(url_for('admin.criar_cliente'))

    # GET: Busca os módulos disponíveis para preencher o select no HTML
    modules_res = supabase.table("modules").select("*").execute()
    return render_template('admin/form_cliente.html', modules=modules_res.data)

@admin_bp.route('/clientes/status/<tenant_id>/<novo_status>', methods=['POST'])
def alterar_status(tenant_id, novo_status):
    """Altera o status da licença (active, suspended, archived)."""
    try:
        admin_supabase.table("tenants").update({"status": novo_status}).eq("id", tenant_id).execute()
        flash(f"Status do cliente atualizado para {novo_status}.")
    except Exception as e:
        flash(f"Erro ao atualizar status: {e}")
    return redirect(url_for('admin.gerenciar_clientes'))