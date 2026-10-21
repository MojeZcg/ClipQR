"""QR de pago EMVCo: Pix, Transferencias 3.0 y validadores."""
import pytest

from clipqr.fiscal.ids import cbu_valid, cnpj_valid, cpf_valid, iban_valid
from clipqr.payloads import analyze
from clipqr.payments import crc16, parse_tlv

# Ejemplo oficial del manual de Pix del Banco Central do Brasil
PIX = ("00020126580014br.gov.bcb.pix0136123e4567-e12b-12d1-a456-4266554400005204000053039865802BR"
       "5913Fulano de Tal6008BRASILIA62070503***63041D3D")
CVU = "0000003110001000000004"


def tlv(*pairs):
    return "".join(f"{tag}{len(value):02d}{value}" for tag, value in pairs)


def emv(*pairs, init="11"):
    """Código EMV con CRC correcto; init «12» = QR de un solo cobro."""
    body = tlv(("00", "01"), ("01", init), *pairs) + "6304"
    return body + crc16(body)


def test_crc_del_ejemplo_oficial():
    assert crc16(PIX[:-4]) == "1D3D"


def test_pix_oficial():
    r = analyze(PIX)
    assert r.kind == "payment" and r.title == "Pago QR · Pix"
    items = dict(r.items)
    assert items["Cobra"] == "Fulano de Tal" and items["Ciudad"] == "BRASILIA" and items["País"] == "Brasil"
    assert items["Clave Pix"] == "123e4567-e12b-12d1-a456-426655440000"
    assert "Referencia" not in items  # «***» = sin referencia
    assert r.headline == ("Cobra", "Fulano de Tal")
    assert not r.warnings
    assert r.actions[0] == ("Copiar código de pago", "copy", PIX)
    assert ("Copiar clave Pix", "copy", "123e4567-e12b-12d1-a456-426655440000") in r.actions


def test_pix_con_importe_y_cpf_invalido():
    text = emv(("26", tlv(("00", "br.gov.bcb.pix"), ("01", "52998224724"))), ("52", "0000"), ("53", "986"),
               ("54", "1234.50"), ("58", "BR"), ("59", "Loja Teste"), ("60", "SAO PAULO"))
    r = analyze(text)
    assert r.headline == ("Importe", "R$ 1.234,50")
    assert r.subtitle == "Para Loja Teste"
    assert any("CPF" in w for w in r.warnings)


def test_transferencias_3_argentina():
    cvu_item = tlv(("00", "com.mercadopago"), ("01", CVU))
    text = emv(("43", cvu_item), ("52", "5411"), ("53", "032"), ("54", "15000"), ("58", "AR"),
               ("59", "Almacen Prueba"), ("60", "CABA"), ("62", tlv(("05", "PED-77"))), init="12")
    r = analyze(text)
    items = dict(r.items)
    assert r.title == "Pago QR · Mercado Pago"
    assert r.headline == ("Importe", "$ 15.000,00")
    assert items["CVU"] == CVU and items["Referencia"] == "PED-77" and items["Tipo"] == "QR de un solo cobro"
    assert ("Copiar CVU", "copy", CVU) in r.actions
    assert not r.warnings


def test_cvu_invalido():
    bad = CVU[:-1] + "8"
    text = emv(("26", tlv(("00", "ar.com.modo"), ("01", bad))), ("53", "032"), ("58", "AR"), ("59", "X"))
    r = analyze(text)
    assert r.title == "Pago QR · MODO"
    assert any("CVU" in w for w in r.warnings)


def test_crc_alterado():
    r = analyze(PIX.replace("Fulano", "Fulana"))
    assert r.kind == "payment"
    assert any("alterado" in w for w in r.warnings)


def test_estructura_rota_no_rompe():
    r = analyze("000201269999br.gov6304ABCD")
    assert r.kind == "payment" and r.warnings


@pytest.mark.parametrize("text", ["000201 hola", "hola 63041D3D", "https://example.com/000201"])
def test_no_es_pago(text):
    assert analyze(text).kind != "payment"


def test_parse_tlv():
    assert parse_tlv("0002010102AB") == [("00", "01"), ("01", "AB")]
    assert parse_tlv("0099x") is None


@pytest.mark.parametrize("cbu, ok", [(CVU, True), ("0110599550000001234560", True),
                                     ("0110599550000001234561", False), ("0110599450000001234560", False),
                                     ("123", False), ("011059955000000123456X", False)])
def test_cbu(cbu, ok):
    assert cbu_valid(cbu) is ok


@pytest.mark.parametrize("cpf, ok", [("529.982.247-25", True), ("52998224725", True), ("529.982.247-24", False),
                                     ("111.111.111-11", False), ("123", False)])
def test_cpf(cpf, ok):
    assert cpf_valid(cpf) is ok


@pytest.mark.parametrize("cnpj, ok", [("11.222.333/0001-81", True), ("11.222.333/0001-80", False),
                                      ("00.000.000/0000-00", False)])
def test_cnpj(cnpj, ok):
    assert cnpj_valid(cnpj) is ok


# ---------------------------------------------------------------- SEPA y QR-factura suiza

# Ejemplo de las directrices del EPC (EPC069-12)
EPC = "BCD\n002\n1\nSCT\nBPOTBEB1\nRed Cross of Belgium\nBE72000000001616\nEUR1\nCHAR\n\nUrgency fund\nSample"


def test_iban():
    assert iban_valid("BE72000000001616") and iban_valid("DE89 3704 0044 0532 0130 00")
    assert not iban_valid("DE89370400440532013001") and not iban_valid("hola")


def test_sepa():
    r = analyze(EPC)
    items = dict(r.items)
    assert r.kind == "payment" and r.title == "Transferencia SEPA"
    assert r.headline == ("Importe", "1,00 €")
    assert items["IBAN"] == "BE72 0000 0000 1616" and items["BIC"] == "BPOTBEB1"
    assert items["Motivo"] == "Donación" and items["Concepto"] == "Urgency fund"
    assert r.actions[0] == ("Copiar IBAN", "copy", "BE72000000001616")
    assert not r.warnings


def test_sepa_iban_alterado_y_sin_importe():
    r = analyze(EPC.replace("BE72000000001616", "BE72000000001617").replace("EUR1\n", "\n"))
    assert any("IBAN" in w for w in r.warnings)
    assert r.headline == ("Beneficiario", "Red Cross of Belgium")


def test_qr_factura_suiza():
    lines = ["SPC", "0200", "1", "CH4431999123000889012", "S", "Robert Schneider AG", "Rue du Lac", "1268",
             "2501", "Biel", "CH", "", "", "", "", "", "", "", "1949.75", "CHF", "S", "Pia-Maria Rutschmann",
             "Grosse Marktgasse", "28", "9400", "Rorschach", "CH", "QRR", "210000000003139471430009017",
             "Pedido del 15.10.2026", "EPD"]
    r = analyze("\n".join(lines))
    items = dict(r.items)
    assert r.title == "QR-factura suiza"
    assert r.headline == ("Importe", "CHF 1'949.75")
    assert items["Beneficiario"] == "Robert Schneider AG" and items["Localidad"] == "2501 Biel"
    assert items["Tipo de referencia"] == "Referencia QR"
    assert ("Copiar referencia", "copy", "210000000003139471430009017") in r.actions
    assert not r.warnings
