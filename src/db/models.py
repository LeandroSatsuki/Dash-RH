from __future__ import annotations

from datetime import UTC, date, datetime, time
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, Time
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


class Jornada(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "jornadas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    carga_horaria_semanal: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    carga_horaria_diaria: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    tolerancia_entrada_minutos: Mapped[int | None] = mapped_column(Integer)
    tolerancia_saida_minutos: Mapped[int | None] = mapped_column(Integer)
    intervalo_minimo_minutos: Mapped[int | None] = mapped_column(Integer)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Turno(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "turnos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    jornada_id: Mapped[int] = mapped_column(ForeignKey("jornadas.id"), nullable=False)
    dia_semana: Mapped[int] = mapped_column(Integer, nullable=False)
    hora_entrada: Mapped[time | None] = mapped_column(Time)
    hora_saida_intervalo: Mapped[time | None] = mapped_column(Time)
    hora_retorno_intervalo: Mapped[time | None] = mapped_column(Time)
    hora_saida: Mapped[time | None] = mapped_column(Time)
    descanso: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    noturno: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ColaboradorJornada(Base, TimestampMixin):
    __tablename__ = "colaborador_jornadas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    jornada_id: Mapped[int] = mapped_column(ForeignKey("jornadas.id"), nullable=False)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date | None] = mapped_column(Date)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)


class MarcacaoPonto(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "marcacoes_ponto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    horario: Mapped[time] = mapped_column(Time, nullable=False)
    origem: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    observacao: Mapped[str | None] = mapped_column(Text)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))


class ApuracaoPonto(Base, TimestampMixin):
    __tablename__ = "apuracoes_ponto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    jornada_id: Mapped[int | None] = mapped_column(ForeignKey("jornadas.id"))
    horas_previstas: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    horas_trabalhadas: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    horas_extras: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    horas_faltantes: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    atraso_minutos: Mapped[int | None] = mapped_column(Integer)
    saida_antecipada_minutos: Mapped[int | None] = mapped_column(Integer)
    adicional_noturno_horas: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    falta: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pendente", nullable=False)


class AjustePonto(Base, TimestampMixin):
    __tablename__ = "ajustes_ponto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    tipo_ajuste: Mapped[str] = mapped_column(String(100), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    valor_anterior: Mapped[str | None] = mapped_column(Text)
    valor_novo: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pendente", nullable=False)
    solicitante_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    aprovador_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))


class BancoHorasMovimento(Base, TimestampMixin):
    __tablename__ = "banco_horas_movimentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    origem: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    horas: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    competencia_id: Mapped[int | None] = mapped_column(ForeignKey("competencias_folha.id"))


class ConfiguracaoSistema(Base, TimestampMixin):
    __tablename__ = "configuracoes_sistema"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chave: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    valor: Mapped[str] = mapped_column(Text, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)


class TipoDocumento(Base, TimestampMixin):
    __tablename__ = "tipos_documento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    descricao: Mapped[str | None] = mapped_column(Text)
    sensivel: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    exige_validade: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class DocumentoObrigatorioRegra(Base, TimestampMixin):
    __tablename__ = "documentos_obrigatorios_regras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo_documento_id: Mapped[int] = mapped_column(ForeignKey("tipos_documento.id"), nullable=False)
    regime_contratual: Mapped[str | None] = mapped_column(String(50))
    cargo_id: Mapped[int | None] = mapped_column(ForeignKey("cargos.id"))
    departamento_id: Mapped[int | None] = mapped_column(ForeignKey("departamentos.id"))
    obrigatorio: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    validade_dias: Mapped[int | None] = mapped_column(Integer)


class DocumentoPendencia(Base, TimestampMixin):
    __tablename__ = "documentos_pendencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    tipo_documento_id: Mapped[int] = mapped_column(ForeignKey("tipos_documento.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pendente", nullable=False)
    data_vencimento: Mapped[date | None] = mapped_column(Date)
    severidade: Mapped[str] = mapped_column(String(50), default="media", nullable=False)
    resolvido_em: Mapped[datetime | None] = mapped_column(DateTime)
    justificativa: Mapped[str | None] = mapped_column(Text)


class ExameOcupacional(Base, TimestampMixin):
    __tablename__ = "exames_ocupacionais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    tipo_exame: Mapped[str] = mapped_column(String(50), nullable=False)
    data_exame: Mapped[date] = mapped_column(Date, nullable=False)
    data_validade: Mapped[date | None] = mapped_column(Date)
    clinica: Mapped[str | None] = mapped_column(String(255))
    resultado: Mapped[str | None] = mapped_column(Text)
    documento_id: Mapped[int | None] = mapped_column(ForeignKey("documentos.id"))
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)


class EPI(Base, TimestampMixin):
    __tablename__ = "epis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    ca: Mapped[str | None] = mapped_column(String(50))
    validade_ca: Mapped[date | None] = mapped_column(Date)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class EntregaEPI(Base, TimestampMixin):
    __tablename__ = "entregas_epi"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    epi_id: Mapped[int] = mapped_column(ForeignKey("epis.id"), nullable=False)
    data_entrega: Mapped[date] = mapped_column(Date, nullable=False)
    data_devolucao: Mapped[date | None] = mapped_column(Date)
    quantidade: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    termo_documento_id: Mapped[int | None] = mapped_column(ForeignKey("documentos.id"))
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)


class TreinamentoSST(Base, TimestampMixin):
    __tablename__ = "treinamentos_sst"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    validade_meses: Mapped[int | None] = mapped_column(Integer)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ColaboradorTreinamentoSST(Base, TimestampMixin):
    __tablename__ = "colaborador_treinamentos_sst"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), nullable=False)
    treinamento_id: Mapped[int] = mapped_column(ForeignKey("treinamentos_sst.id"), nullable=False)
    data_realizacao: Mapped[date] = mapped_column(Date, nullable=False)
    data_validade: Mapped[date | None] = mapped_column(Date)
    documento_id: Mapped[int | None] = mapped_column(ForeignKey("documentos.id"))
    status: Mapped[str] = mapped_column(String(50), default="ativo", nullable=False)


class Alerta(Base, TimestampMixin):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    severidade: Mapped[str] = mapped_column(String(50), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    entidade_tipo: Mapped[str | None] = mapped_column(String(100))
    entidade_id: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="aberto", nullable=False)
    resolvido_em: Mapped[datetime | None] = mapped_column(DateTime)
    usuario_responsavel_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    justificativa: Mapped[str | None] = mapped_column(Text)


class Workflow(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class WorkflowEtapa(Base, TimestampMixin):
    __tablename__ = "workflow_etapas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    perfil_responsavel: Mapped[str | None] = mapped_column(String(50))
    permissao_requerida: Mapped[str | None] = mapped_column(String(100))
    obrigatoria: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prazo_horas: Mapped[int | None] = mapped_column(Integer)
    permite_reprovar: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    permite_devolver: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class WorkflowInstancia(Base, TimestampMixin):
    __tablename__ = "workflow_instancias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    entidade_tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="rascunho", nullable=False)
    etapa_atual_id: Mapped[int | None] = mapped_column(ForeignKey("workflow_etapas.id"))
    solicitante_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    responsavel_atual_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime)
    cancelado_em: Mapped[datetime | None] = mapped_column(DateTime)


class WorkflowHistorico(Base):
    __tablename__ = "workflow_historico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    instancia_id: Mapped[int] = mapped_column(ForeignKey("workflow_instancias.id"), nullable=False)
    etapa_id: Mapped[int | None] = mapped_column(ForeignKey("workflow_etapas.id"))
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    acao: Mapped[str] = mapped_column(String(50), nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)


class Tarefa(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    modulo: Mapped[str] = mapped_column(String(50), nullable=False)
    entidade_tipo: Mapped[str | None] = mapped_column(String(100))
    entidade_id: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="aberta", nullable=False)
    prioridade: Mapped[str] = mapped_column(String(20), default="media", nullable=False)
    responsavel_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    solicitante_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    prazo: Mapped[datetime | None] = mapped_column(DateTime)
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime)
    motivo_cancelamento: Mapped[str | None] = mapped_column(Text)


class TarefaComentario(Base):
    __tablename__ = "tarefas_comentarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tarefa_id: Mapped[int] = mapped_column(ForeignKey("tarefas.id"), nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    comentario: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)


class TarefaAnexo(Base):
    __tablename__ = "tarefas_anexos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tarefa_id: Mapped[int] = mapped_column(ForeignKey("tarefas.id"), nullable=False)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    severidade: Mapped[str] = mapped_column(String(20), default="info", nullable=False)
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    link_entidade_tipo: Mapped[str | None] = mapped_column(String(100))
    link_entidade_id: Mapped[int | None] = mapped_column(Integer)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow_naive, nullable=False)
    lida_em: Mapped[datetime | None] = mapped_column(DateTime)


class ConfiguracaoNotificacao(Base, TimestampMixin):
    __tablename__ = "configuracoes_notificacao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canal: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    config_json: Mapped[dict | None] = mapped_column(JSON)
