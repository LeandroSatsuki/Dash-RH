from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


def utcnow_naive() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class TimestampMixin:
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, onupdate=utcnow_naive, nullable=False)


class SoftDeleteMixin:
    deletado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    perfil: Mapped[str] = mapped_column(String(50), nullable=False, default="visualizador")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, onupdate=utcnow_naive, nullable=False)


class Empresa(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    razao_social: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_fantasia: Mapped[str | None] = mapped_column(String(255))
    cnpj: Mapped[str | None] = mapped_column(String(18), unique=True)
    status: Mapped[str] = mapped_column(String(50), default="ativa", nullable=False)


class Departamento(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "departamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    gestor_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)


class Cargo(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "cargos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cbo: Mapped[str | None] = mapped_column(String(20))
    departamento_id: Mapped[int | None] = mapped_column(ForeignKey("departamentos.id"))
    descricao: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)


class CentroCusto(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "centros_custo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[str | None] = mapped_column(String(255))
    subarea: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)


class Colaborador(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "colaboradores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    matricula: Mapped[str | None] = mapped_column(String(50), unique=True)
    nome_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_social: Mapped[str | None] = mapped_column(String(255))
    cpf: Mapped[str | None] = mapped_column(String(14), index=True)
    rg: Mapped[str | None] = mapped_column(String(30))
    data_nascimento: Mapped[date | None] = mapped_column(Date)
    email: Mapped[str | None] = mapped_column(String(255))
    telefone: Mapped[str | None] = mapped_column(String(30))
    endereco: Mapped[str | None] = mapped_column(Text)
    cidade: Mapped[str | None] = mapped_column(String(255))
    uf: Mapped[str | None] = mapped_column(String(2))
    regime_contratual: Mapped[str | None] = mapped_column(String(50))
    tipo_vinculo: Mapped[str | None] = mapped_column(String(50))
    data_admissao: Mapped[date | None] = mapped_column(Date)
    data_desligamento: Mapped[date | None] = mapped_column(Date)
    cargo_id: Mapped[int | None] = mapped_column(ForeignKey("cargos.id"))
    departamento_id: Mapped[int | None] = mapped_column(ForeignKey("departamentos.id"))
    centro_custo_id: Mapped[int | None] = mapped_column(ForeignKey("centros_custo.id"))
    salario_base: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    jornada_semanal: Mapped[float | None] = mapped_column(Float)
    gestor_id: Mapped[int | None] = mapped_column(ForeignKey("colaboradores.id"))
    status: Mapped[str] = mapped_column(String(50), default="pre_admissao", nullable=False)
    origem: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)


class HistoricoFuncional(Base):
    __tablename__ = "historico_funcional"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False, index=True)
    tipo_evento: Mapped[str] = mapped_column(String(100), nullable=False)
    data_evento: Mapped[date] = mapped_column(Date, nullable=False)
    data_inicio: Mapped[date | None] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    campo_alterado: Mapped[str | None] = mapped_column(String(255))
    valor_anterior: Mapped[str | None] = mapped_column(Text)
    valor_novo: Mapped[str | None] = mapped_column(Text)
    motivo: Mapped[str | None] = mapped_column(Text)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)


class Admissao(Base, TimestampMixin):
    __tablename__ = "admissoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    data_prevista_admissao: Mapped[date | None] = mapped_column(Date)
    data_admissao: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default="rascunho", nullable=False)
    checklist_json: Mapped[dict | None] = mapped_column(JSON)
    observacao: Mapped[str | None] = mapped_column(Text)


class Ferias(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "ferias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    periodo_aquisitivo_inicio: Mapped[date | None] = mapped_column(Date)
    periodo_aquisitivo_fim: Mapped[date | None] = mapped_column(Date)
    data_limite_gozo: Mapped[date | None] = mapped_column(Date)
    dias_direito: Mapped[float | None] = mapped_column(Float)
    dias_gozados: Mapped[float | None] = mapped_column(Float)
    dias_restantes: Mapped[float | None] = mapped_column(Float)
    data_inicio: Mapped[date | None] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    abono_pecuniario: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    adiantamento_13: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="planejada", nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)


class Afastamento(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "afastamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date)
    quantidade_dias: Mapped[float | None] = mapped_column(Float)
    quantidade_horas: Mapped[float | None] = mapped_column(Float)
    impacta_folha: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    impacta_absenteismo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cid_mascarado: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)


class Beneficio(Base, TimestampMixin):
    __tablename__ = "beneficios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str | None] = mapped_column(String(100))
    operadora: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)


class ColaboradorBeneficio(Base, TimestampMixin):
    __tablename__ = "colaborador_beneficios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    beneficio_id: Mapped[int] = mapped_column(ForeignKey("beneficios.id"), nullable=False)
    data_inicio: Mapped[date | None] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    valor_empresa: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    valor_colaborador: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    dependentes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)


class CompetenciaFolha(Base, TimestampMixin):
    __tablename__ = "competencias_folha"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    competencia: Mapped[str] = mapped_column(String(7), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="aberta", nullable=False)
    data_abertura: Mapped[datetime | None] = mapped_column(DateTime)
    data_fechamento: Mapped[datetime | None] = mapped_column(DateTime)
    usuario_fechamento_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    observacao: Mapped[str | None] = mapped_column(Text)


class Rubrica(Base, TimestampMixin):
    __tablename__ = "rubricas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    natureza: Mapped[str | None] = mapped_column(String(100))
    incide_inss: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    incide_fgts: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    incide_irrf: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class LancamentoFolha(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "lancamentos_folha"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("competencias_folha.id"), nullable=False)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    rubrica_id: Mapped[int] = mapped_column(ForeignKey("rubricas.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    quantidade: Mapped[float | None] = mapped_column(Float)
    origem: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)


class Desligamento(Base, TimestampMixin):
    __tablename__ = "desligamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    data_aviso_previo: Mapped[date | None] = mapped_column(Date)
    data_desligamento: Mapped[date | None] = mapped_column(Date)
    tipo_rescisao: Mapped[str | None] = mapped_column(String(100))
    motivo: Mapped[str | None] = mapped_column(Text)
    exame_demissional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    entrevista_realizada: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="rascunho", nullable=False)
    valor_estimado_rescisao: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    observacao: Mapped[str | None] = mapped_column(Text)


class Documento(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(100), nullable=False)
    nome_original: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_armazenado: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho_arquivo: Mapped[str] = mapped_column(String(500), nullable=False)
    hash_arquivo: Mapped[str] = mapped_column(String(128), nullable=False)
    validade: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)
    usuario_upload_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    tabela: Mapped[str] = mapped_column(String(255), nullable=False)
    registro_id: Mapped[int | None] = mapped_column(Integer)
    acao: Mapped[str] = mapped_column(String(100), nullable=False)
    campo_alterado: Mapped[str | None] = mapped_column(String(255))
    valor_anterior: Mapped[str | None] = mapped_column(Text)
    valor_novo: Mapped[str | None] = mapped_column(Text)
    ip: Mapped[str | None] = mapped_column(String(64))
    origem: Mapped[str | None] = mapped_column(String(100))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)


class Importacao(Base):
    __tablename__ = "importacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_importacao: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pendente")
    total_linhas: Mapped[int | None] = mapped_column(Integer)
    linhas_importadas: Mapped[int | None] = mapped_column(Integer)
    linhas_com_erro: Mapped[int | None] = mapped_column(Integer)
    relatorio_erros: Mapped[dict | None] = mapped_column(JSON)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)


class FolhaSnapshot(Base):
    __tablename__ = "folha_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competencia_id: Mapped[int] = mapped_column(ForeignKey("competencias_folha.id"), nullable=False, unique=True)
    total_proventos: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_descontos: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_encargos: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_beneficios: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_liquido_estimado: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total_custo_empresa: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    quantidade_colaboradores: Mapped[int | None] = mapped_column(Integer)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
