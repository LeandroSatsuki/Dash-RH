from fastapi import HTTPException

from src.auth.permissions import has_permission, require_permission


def test_permissions_matrix():
    assert has_permission("admin", "qualquer:coisa")
    assert has_permission("dp", "colaboradores:create")
    assert not has_permission("visualizador", "colaboradores:create")


def test_require_permission():
    user = {"perfil": "visualizador"}
    try:
        require_permission(user, "folha:create")
        assert False, "Era esperado erro"
    except HTTPException as exc:
        assert exc.status_code == 403
