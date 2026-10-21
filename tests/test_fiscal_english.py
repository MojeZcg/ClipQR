"""Facturas en inglés: los textos propios de cada país salen traducidos (los de Comprobante no se miran)."""
import base64
import json

import pytest

from clipqr import i18n
from clipqr.fiscal import br_nfe, cl_sii, mx_cfdi, uy_dgi
from clipqr.fiscal.es_ticketbai import parse_ticketbai
from clipqr.fiscal.es_verifactu import parse_verifactu
from clipqr.fiscal.pt_atcud import parse_atcud
from clipqr.payloads import analyze

ARCA = {"ver": 1, "fecha": "2025-10-13", "cuit": 33693450239, "ptoVta": 3, "tipoCmp": 6, "nroCmp": 1234,
        "importe": 12345.67, "moneda": "PES", "ctz": 1, "tipoDocRec": 96, "nroDocRec": 12345678,
        "tipoCodAut": "E", "codAut": 74123456789012}
MX = ("https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?id=5803EB8D-81CD-4557-8719-26632D2FA434"
      "&re=XOCD720319T86&rr=XAXX010101000&tt=1234.5&fe=rH8/bw==")
VF = ("https://www2.agenciatributaria.gob.es/wlpl/TIKE-CONT/ValidarQR?nif=89890001K&numserie=12345678-G33"
      "&fecha=01-09-2024&importe=241.4")
TBAI = "https://batuz.eus/QRTBAI/?id=TBAI-00000006Y-251019-btFpwP8dcLGAF-237&s=T&nf=27174&i=4.70&cr=007"
PT_FS = ("A:123456789*B:999999990*C:PT*D:FS*E:N*F:20190812*G:FS CDVF/12345*H:CDF7T5HD-12345*I1:PT"
         "*I7:0.65*I8:0.15*N:0.15*O:0.80*Q:YhGV*R:9999*S:NU;0.80")
CHAVE = "43150108287693000157651010000000971000001251"
BR = f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p={CHAVE}|2|1|1|ecc4f0e7e612456f2e3521768bd572b6f0eae240"


@pytest.fixture(autouse=True)
def english():
    i18n.set_language("en")


def arca(**changes):
    p = base64.b64encode(json.dumps(dict(ARCA, **changes)).encode()).decode()
    return f"https://www.afip.gob.ar/fe/qr/?p={p}"


def test_arca_factura_b():
    r = analyze(arca())
    assert r.subtitle == "Invoice B · 00003-00001234 · 13/10/2025"
    d = dict(r.items)
    assert d["Issuer CUIT"] == "33-69345023-9" and d["Recipient DNI"] == "12345678"
    labels = [a[0] for a in r.actions]
    assert "Verify document with ARCA ↗" in labels and "Copy details for verification" in labels
    datos = next(a[2] for a in r.actions if a[0] == "Copy details for verification")
    assert "Issuer CUIT: 33693450239" in datos and "Point of sale: 3" in datos


def test_arca_avisos():
    r = analyze(arca(cuit=33693450238, codAut=123, fecha="2099-01-01"))
    assert "The issuer's CUIT is not valid (check digit)" in r.warnings
    assert "The CAE is missing or does not have 14 digits" in r.warnings
    assert "The document date is in the future" in r.warnings
    assert analyze("https://www.afip.gob.ar/fe/qr/?p=xx").warnings == [
        "Invoice QR is incomplete or has been modified"]


def test_mexico():
    r = mx_cfdi.parse_mx_cfdi(MX)
    d = dict(r.items)
    assert d["Issuer RFC"] == "XOCD720319T86"
    assert d["Recipient RFC"] == "XAXX010101000 (general public)"
    assert d["Tax folio (UUID)"].startswith("5803EB8D")
    assert r.subtitle.startswith("Invoice (CFDI)")
    r = mx_cfdi.parse_mx_cfdi(MX.replace("XOCD720319T86", "XOCD720319T87"))
    assert "The issuer's RFC (XOCD720319T87) is not valid: the QR may have been modified" in r.warnings


def test_chile_y_uruguay():
    cl = ("<TED version=\"1.0\"><DD><RE>97975000-5</RE><TD>39</TD><F>60</F><FE>2003-10-13</FE>"
          "<MNT>119000</MNT></DD><FRMT>x</FRMT></TED>")
    assert cl_sii.parse_cl_sii(cl).subtitle == "Electronic receipt (boleta) · No. 60 · 13/10/2003"
    assert uy_dgi.tipo_cfe("211") == "e-Factura (contingency)"
    assert uy_dgi.tipo_cfe("112") == "e-Invoice credit note"


def test_espana():
    r = parse_verifactu(VF)
    assert dict(r.items)["Issuer NIF"] == "89890001K"
    assert dict(r.items)["Mode"] == "VERI*FACTU (verifiable with the AEAT)"
    assert r.subtitle.startswith("Invoice · ")
    r = parse_verifactu(VF.replace("ValidarQR?", "ValidarQRNoVerifactu?"))
    assert "AEAT (non-VERI*FACTU)" in r.title
    r = parse_ticketbai(TBAI.replace("i=4.70", "i=47.00"))
    assert "TicketBAI QR has been altered: the check code does not match" in r.warnings
    assert dict(r.items)["Territory"] == "Bizkaia"


def test_portugal():
    r = parse_atcud(PT_FS)
    assert r.subtitle.startswith("Simplified invoice · ")
    d = dict(r.items)
    assert d["Issuer NIF"] == "123456789" and d["Buyer NIF"] == "Final consumer"
    assert "Total taxes" in d and "Software certificate" in d
    assert "Cancelled document" in parse_atcud(PT_FS.replace("*E:N*", "*E:A*")).warnings


def test_brasil():
    r = br_nfe.parse_br_nfe(BR)
    d = dict(r.items)
    assert d["Issuer CNPJ"] == "08.287.693/0001-57"
    assert d["Series"] == "101" and d["State"] == "RS" and d["Month of issue"] == "01/2015"
    assert d["Access key"].startswith("4315 0108 2876")
    assert any(a[0] == "Copy access key" for a in r.actions)
    malo = br_nfe.parse_br_nfe(BR.replace("08287693000157", "08287693000158"))
    assert any(w.startswith("The access key fails the check digit") for w in malo.warnings)
