from src.services.masking import mask_bank_account, mask_cnpj, mask_cpf, mask_email, mask_phone


def test_mask_cpf():
    assert mask_cpf("12345678901") == "***.***.***-01"


def test_mask_cnpj():
    assert mask_cnpj("12345678000199") == "**.***.***/****-99"


def test_mask_email():
    assert mask_email("pessoa@empresa.com").startswith("pe***@")


def test_mask_phone():
    assert mask_phone("11987654321").endswith("4321")


def test_mask_bank_account():
    assert mask_bank_account("12345").endswith("345")
