from __future__ import annotations

from contextlib import contextmanager
from typing import Callable

import streamlit as st

from src.db.init_db import init_db
from src.db.session import SessionLocal
from src.utils.money import format_brl


init_db()


@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def show_success(message: str) -> None:
    st.success(message)


def show_error(message: str) -> None:
    st.error(message)


def show_warning(message: str) -> None:
    st.warning(message)


def confirm_action(label: str, key: str) -> bool:
    return st.checkbox(label, key=key)


def safe_run(action: Callable, *, success_message: str | None = None, error_prefix: str = "Nao foi possivel concluir a operacao."):
    try:
        result = action()
        if success_message:
            show_success(success_message)
        return result
    except Exception as exc:
        show_error(f"{error_prefix} {exc}")
        return None


def format_currency(value) -> str:
    return format_brl(value)


def format_percent(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"{float(value) * 100:.2f}%"


def render_kpi_card(label: str, value, help_text: str | None = None) -> None:
    st.metric(label, value, help=help_text)
