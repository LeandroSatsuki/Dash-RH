from __future__ import annotations

import streamlit as st

from operational_app.common import db_session
from src.auth.permissions import has_permission
from src.auth.security import create_access_token
from src.auth.users import authenticate_user
from src.crud import notificacoes as crud_notificacoes
from src.utils.config import is_development


def get_current_user() -> dict | None:
    return st.session_state.get("current_user")


def can_access(permission: str) -> bool:
    user = get_current_user()
    return bool(user and has_permission(user["perfil"], permission))


def logout() -> None:
    st.session_state.pop("current_user", None)
    st.session_state.pop("access_token", None)


def require_streamlit_login() -> dict | None:
    st.sidebar.header("Acesso")
    current_user = get_current_user()
    if current_user:
        st.sidebar.success(f"Usuario: {current_user['nome']}")
        st.sidebar.caption(f"Perfil: {current_user['perfil']}")
        st.sidebar.caption(f"Nao lidas: {current_user.get('unread_notifications', 0)}")
        if st.sidebar.button("Logout"):
            logout()
            st.rerun()
        return current_user

    with st.sidebar.form("login_operacional"):
        email = st.text_input("E-mail", value="admin@local.test" if is_development() else "")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")
    if entrar:
        with db_session() as db:
            user = authenticate_user(db, email, senha)
            if user is None:
                st.sidebar.error("Credenciais invalidas.")
            else:
                unread = len(crud_notificacoes.listar(db, usuario_id=user.id, apenas_nao_lidas=True))
                st.session_state["current_user"] = {"id": user.id, "nome": user.nome, "email": user.email, "perfil": user.perfil, "unread_notifications": unread}
                st.session_state["access_token"] = create_access_token({"user_id": user.id, "perfil": user.perfil, "email": user.email})
                st.rerun()
    return None
