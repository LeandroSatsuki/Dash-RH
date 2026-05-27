"""notifications tables

Revision ID: f1a2b3c4d5e6
Revises: aa80f1838f9d
Create Date: 2026-05-26 14:31:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "f1a2b3c4d5e6"
down_revision = "aa80f1838f9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notificacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("tipo", sa.String(length=50), nullable=False),
        sa.Column("severidade", sa.String(length=20), nullable=False),
        sa.Column("lida", sa.Boolean(), nullable=False),
        sa.Column("link_entidade_tipo", sa.String(length=100), nullable=True),
        sa.Column("link_entidade_id", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("lida_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "configuracoes_notificacao",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("canal", sa.String(length=50), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("canal"),
    )


def downgrade() -> None:
    op.drop_table("configuracoes_notificacao")
    op.drop_table("notificacoes")
