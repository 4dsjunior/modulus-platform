from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
import os
import gotrue.errors

auth_bp = Blueprint('auth', __name__)

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
try:
    supabase: Client = create_client(supabase_url, supabase_key)
except:
    supabase = None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # 1. Autenticação Padrão (Supabase)
            auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = auth_response.user

            # Limpa sessão para começar limpo
            session.clear()
            session.permanent = True
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['access_token'] = auth_response.session.access_token

            # ==============================================================================
            # PASSO 1: VERIFICAÇÃO DE SUPERADMIN (PRIORIDADE TOTAL)
            # ==============================================================================
            # Tenta buscar o perfil. Usamos maybe_single() para não quebrar se não existir.
            profile_resp = supabase.table('profiles')\
                .select('is_super_admin')\
                .eq('id', user.id)\
                .maybe_single()\
                .execute()
            
            # LÓGICA SIMPLES: Se tem perfil E a flag é verdadeira -> É Admin.
            if profile_resp.data and profile_resp.data.get('is_super_admin') is True:
                print(f"LOGIN ADMIN DETECTADO: {email}")
                session['is_super_admin'] = True  # Chave Mestra para o admin.py
                session['role'] = 'super_admin'
                return redirect(url_for('admin.clientes')) # Rota direta para gestão de clientes

            # ==============================================================================
            # PASSO 2: NÃO É ADMIN? ENTÃO VERIFICA UNIDADES E MÓDULOS
            # ==============================================================================
            print(f"LOGIN COMUM: Verificando unidades para {email}")
            
            # Busca unidades vinculadas
            members_resp = supabase.table('tenant_members')\
                .select('tenant_id, role, tenants(name)')\
                .eq('user_id', user.id)\
                .execute()
            
            # Se não tem unidade, tchau.
            if not members_resp.data:
                flash('Acesso negado: Usuário sem unidades vinculadas.', 'warning')
                return redirect(url_for('auth.login'))

            # Busca módulos ativos para essas unidades
            tenant_ids = [m['tenant_id'] for m in members_resp.data]
            modules_resp = supabase.table('tenant_modules')\
                .select('tenant_id, module_id, modules(name)')\
                .in_('tenant_id', tenant_ids)\
                .eq('is_enabled', True)\
                .execute()

            # Monta lista de acesso (Portal)
            options = []
            for mod in modules_resp.data:
                # Acha o nome da unidade correspondente
                nome_unidade = next((t['tenants']['name'] for t in members_resp.data if t['tenant_id'] == mod['tenant_id']), "Unidade")
                
                options.append({
                    'tenant_id': mod['tenant_id'],
                    'tenant_name': nome_unidade,
                    'module_id': mod['module_id'],
                    'module_name': mod['modules']['name']
                })

            if not options:
                flash('Nenhum módulo ativo para suas unidades.', 'warning')
                return redirect(url_for('auth.login'))

            # Se só tem 1 opção, vai direto
            if len(options) == 1:
                opt = options[0]
                session['tenant_id'] = opt['tenant_id']
                session['module_id'] = opt['module_id']
                return redirect(url_for(f"{opt['module_id']}.dashboard"))

            # Se tem várias, Portal
            session['access_options'] = options
            return redirect(url_for('auth.portal'))

        except gotrue.errors.AuthApiError:
            flash("E-mail ou senha incorretos.", 'error')
        except Exception as e:
            print(f"ERRO LOGIN: {e}")
            flash("Erro ao conectar.", 'error')

    return render_template('login.html')

# Rotas auxiliares do Portal continuam as mesmas
@auth_bp.route('/portal')
def portal():
    options = session.get('access_options')
    if not options: return redirect(url_for('auth.login'))
    return render_template('portal.html', options=options)

@auth_bp.route('/select_context/<tenant_id>/<module_id>')
def select_context(tenant_id, module_id):
    options = session.get('access_options', [])
    selected = next((o for o in options if o['tenant_id'] == tenant_id and o['module_id'] == module_id), None)
    if selected:
        session['tenant_id'] = selected['tenant_id']
        session['module_id'] = selected['module_id']
        return redirect(url_for(f"{selected['module_id']}.dashboard"))
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))