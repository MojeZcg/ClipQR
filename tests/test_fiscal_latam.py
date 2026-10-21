"""Comprobantes de Latinoamérica: CFDI (MX), DTE (CL), CPE (PE), DIAN (CO), CFE (UY), NFC-e (BR), SRI (EC).

Los ejemplos salen de los documentos oficiales cuando los hay (Anexo 20 del SAT, XML de ejemplo del SII,
Anexo técnico 1.9 de la DIAN, NT 2025.001 de la NF-e, ficha técnica del SRI); el resto son datos ficticios
con dígitos verificadores correctos."""
import pytest

from clipqr.fiscal import br_nfe, cl_sii, co_dian, ec_sri, mx_cfdi, pe_sunat, uy_dgi
from clipqr.fiscal.comun_latam import AVISO_INCOMPLETO, fecha_dmy
from clipqr.fiscal.ids_latam import (cnpj_valid, cpf_valid, format_cnpj, format_cpf, format_nit, format_rfc,
                                     format_ruc_ec, format_ruc_pe, format_ruc_uy, format_rut, nit_dv,
                                     nit_valid, rfc_valid, ruc_ec_valid, ruc_pe_valid, ruc_uy_valid, rut_valid)
from clipqr.payloads import analyze


def items(r):
    return dict(r.items)


def acciones(r):
    return {a[0]: a[2] for a in r.actions}


# ---------------------------------------------------------------- validadores

@pytest.mark.parametrize("rfc, ok", [
    ("XOCD720319T86", True), ("CARR861127SB0", True), ("EKU9003173C9", True),  # persona física y moral
    ("XAXX010101000", True), ("XEXX010101000", True),                          # genéricos del SAT
    ("XOCD720319T87", False), ("XOCD721319T86", False), ("ABC", False), ("", False),
])
def test_rfc(rfc, ok):
    assert rfc_valid(rfc) is ok


def test_format_rfc():
    assert format_rfc(" xocd720319t86 ") == "XOCD720319T86"


@pytest.mark.parametrize("rut, ok", [
    ("97975000-5", True), ("97.975.000-5", True), ("60803000-K", True), ("60803000k", True),
    ("77777777-7", True), ("97975000-4", False), ("60803000-1", False), ("abc", False), ("", False),
])
def test_rut(rut, ok):
    assert rut_valid(rut) is ok


def test_format_rut():
    assert format_rut("97975000-5") == "97.975.000-5"
    assert format_rut("60803000k") == "60.803.000-K"


@pytest.mark.parametrize("ruc, ok", [
    ("20131312955", True), ("20999999990", True), ("10123456781", True),
    ("20999999991", False), ("30999999990", False), ("2099999999", False), ("", False),
])
def test_ruc_pe(ruc, ok):
    assert ruc_pe_valid(ruc) is ok


def test_format_ruc_pe():
    assert format_ruc_pe("20999999990 ") == "20999999990"


@pytest.mark.parametrize("nit, ok", [
    ("800197268-4", True), ("8001972684", True), ("899.999.034-1", True), ("700085371-1", True),
    ("800197268-5", False), ("123", False), ("", False),
])
def test_nit(nit, ok):
    assert nit_valid(nit) is ok


def test_nit_dv_y_formato():
    assert nit_dv("800197268") == 4
    assert format_nit("800197268") == "800.197.268"
    assert format_nit("8001972684", con_dv=True) == "800.197.268-4"


@pytest.mark.parametrize("ruc, ok", [
    ("219999990016", True), ("211234560019", True), ("21-999999-001-6", True),
    ("219999990017", False), ("229999990012", False), ("219999990026", False), ("21999999001", False),
])
def test_ruc_uy(ruc, ok):
    assert ruc_uy_valid(ruc) is ok


def test_format_ruc_uy():
    assert format_ruc_uy("21-999999-001-6") == "219999990016"


@pytest.mark.parametrize("cpf, ok", [
    ("111.444.777-35", True), ("11144477735", True), ("111.444.777-36", False),
    ("111.111.111-11", False), ("1234", False),
])
def test_cpf(cpf, ok):
    assert cpf_valid(cpf) is ok


@pytest.mark.parametrize("cnpj, ok", [
    ("08.287.693/0001-57", True), ("07385111000102", True), ("12.ABC.345/01DE-35", True),  # alfanumérico
    ("08.287.693/0001-58", False), ("00000000000000", False), ("123", False),
])
def test_cnpj(cnpj, ok):
    assert cnpj_valid(cnpj) is ok


def test_format_cpf_cnpj():
    assert format_cpf("11144477735") == "111.444.777-35"
    assert format_cnpj("08287693000157") == "08.287.693/0001-57"


@pytest.mark.parametrize("ruc, ok", [
    ("1792146739001", True),   # sociedad privada (ejemplo de la ficha técnica del SRI)
    ("1760013210001", True),   # entidad pública
    ("1700000001001", True),   # persona natural (cédula ficticia)
    ("1792146738001", False), ("1700000002001", False), ("9992146739001", False), ("17921467390", False),
])
def test_ruc_ec(ruc, ok):
    assert ruc_ec_valid(ruc) is ok


def test_format_ruc_ec():
    assert format_ruc_ec(" 1792146739001") == "1792146739001"


@pytest.mark.parametrize("texto, esperado", [
    ("2026-10-21", "21/10/2026"), ("20261021", "21/10/2026"), ("21/10/2026", "21/10/2026"),
    ("2019-16-01", None), ("ayer", None), ("", None),
])
def test_fecha_dmy(texto, esperado):
    assert fecha_dmy(texto) == esperado


# ---------------------------------------------------------------- México: CFDI

MX = ("https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?id=5803EB8D-81CD-4557-8719-26632D2FA434"
      "&re=XOCD720319T86&rr=CARR861127SB0&tt=0000014300.000000&fe=rH8/bw==")


def test_mx_ejemplo_del_anexo_20():
    r = mx_cfdi.parse_mx_cfdi(MX)
    assert r.kind == "invoice" and r.warnings == []
    assert r.headline == ("Importe", "$14,300.00")
    d = items(r)
    assert d["RFC emisor"] == "XOCD720319T86" and d["RFC receptor"] == "CARR861127SB0"
    assert d["Folio fiscal (UUID)"] == "5803EB8D-81CD-4557-8719-26632D2FA434"
    assert d["Sello (últimos 8)"] == "rH8/bw=="
    assert acciones(r)["Verificar en el SAT ↗"] == MX


def test_mx_cfdi_32_sin_dominio():
    r = mx_cfdi.parse_mx_cfdi("?re=XOCD720319T86&rr=XAXX010101000&tt=1234.5&id=5803EB8D-81CD-4557-8719-26632D2FA434")
    assert r.headline == ("Importe", "$1,234.50")
    assert items(r)["RFC receptor"] == "XAXX010101000 (público en general)"
    assert acciones(r)["Verificar en el SAT ↗"].startswith("https://verificacfdi.facturaelectronica.sat.gob.mx/")


def test_mx_rfc_alterado():
    r = mx_cfdi.parse_mx_cfdi(MX.replace("XOCD720319T86", "XOCD720319T87"))
    assert any("RFC del emisor" in w for w in r.warnings)


def test_mx_qr_roto():
    r = mx_cfdi.parse_mx_cfdi("https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?id=xx&tt=abc")
    assert AVISO_INCOMPLETO in r.warnings


def test_mx_texto_ajeno():
    assert mx_cfdi.parse_mx_cfdi("https://www.sat.gob.mx/") is None
    assert mx_cfdi.parse_mx_cfdi("hola") is None


# ---------------------------------------------------------------- Chile: DTE

CL = """<TED version="1.0"><DD><RE>97975000-5</RE><TD>33</TD><F>60</F><FE>2003-10-13</FE>
<RR>77777777-7</RR><RSR>EMPRESA  LTDA</RSR><MNT>119000</MNT><IT1>Parlantes Multimedia 180W.</IT1>
<CAF version="1.0"><DA><RE>97975000-5</RE><RS>RUT DE PRUEBA</RS><TD>33</TD><RNG><D>1</D><H>200</H></RNG>
<FA>2003-09-04</FA><RSAPK><M>0a4O6Kbx8Qj3K4iWSP4w7KneZYeJ+g/prihYtIEolKt3cykSxl1zO8vSXu397QhTmsX7SBEudTUx++2zDXBhZw==</M>
<E>Aw==</E></RSAPK><IDK>100</IDK></DA><FRMA algoritmo="SHA1withRSA">g1AQX0sy8NJugX52k2hTJEZAE9Cuul6pqYBdFxj1N17umW7z
G/hAavCALKByHzdYAfZ3LhGTXCai5zNxOo4lDQ==</FRMA></CAF><TSTED>2003-10-13T09:33:20</TSTED></DD>
<FRMT algoritmo="SHA1withRSA">GbmDcS9e/jVC2LsLIe1iRV12Bf6lxsILtbQiCkh6mbjckFCJ7fj/kakFTS06Jo8i
S4HXvJj3oYZuey53Krniew==</FRMT></TED>"""


def test_cl_ejemplo_del_sii():
    r = cl_sii.parse_cl_sii(CL)
    assert r.warnings == []
    assert r.headline == ("Importe", "$ 119.000")
    assert r.subtitle == "Factura electrónica · N° 60 · 13/10/2003"
    d = items(r)
    assert d["RUT emisor"] == "97.975.000-5" and d["RUT receptor"] == "77.777.777-7"
    assert d["Razón social receptor"] == "EMPRESA  LTDA"
    a = acciones(r)
    assert a["Verificar en el SII ↗"] == cl_sii.URL_SII
    assert "Folio: 60" in a["Copiar datos"] and "Monto total: 119000" in a["Copiar datos"]


def test_cl_rut_alterado():
    r = cl_sii.parse_cl_sii(CL.replace("<RE>97975000-5</RE><TD>33", "<RE>97975000-4</RE><TD>33"))
    assert any("RUT del emisor" in w for w in r.warnings)


def test_cl_timbre_cortado():
    r = cl_sii.parse_cl_sii('<TED version="1.0"><DD><RE>97975000-5</RE><TD>39</TD><F>x</F><FE>2003-99-13</FE>')
    assert AVISO_INCOMPLETO in r.warnings
    assert r.subtitle.startswith("Boleta electrónica")


def test_cl_texto_ajeno():
    assert cl_sii.parse_cl_sii("<html><body>hola</body></html>") is None


# ---------------------------------------------------------------- Perú: SUNAT

PE = "20999999990|01|F001|00000123|180.00|1180.00|2026-10-21|6|20123456786|ab12CD34ef56GH78ij90KL12mn3=|"


def test_pe_factura():
    r = pe_sunat.parse_pe_sunat(PE)
    assert r.warnings == []
    assert r.headline == ("Importe", "S/ 1,180.00")
    assert r.subtitle == "Factura electrónica · F001-00000123 · 21/10/2026"
    d = items(r)
    assert d["RUC emisor"] == "20999999990" and d["RUC adquirente"] == "20123456786"
    assert d["IGV"] == "S/ 180.00"
    assert acciones(r)["Verificar en SUNAT ↗"] == pe_sunat.URL_SUNAT


def test_pe_boleta_sin_adquirente():
    r = pe_sunat.parse_pe_sunat("20999999990|03|B001|45|0.00|25.50|21/10/2026|0|-|")
    assert r.warnings == []
    assert r.subtitle == "Boleta de venta electrónica · B001-45 · 21/10/2026"
    assert "Adquirente" not in items(r)


def test_pe_ruc_alterado():
    r = pe_sunat.parse_pe_sunat(PE.replace("20999999990", "20999999991", 1))
    assert any("RUC del emisor" in w for w in r.warnings)


def test_pe_qr_roto():
    r = pe_sunat.parse_pe_sunat("20999999990|01|F001|")
    assert AVISO_INCOMPLETO in r.warnings


def test_pe_texto_ajeno():
    assert pe_sunat.parse_pe_sunat("hola|que|tal") is None


# ---------------------------------------------------------------- Colombia: DIAN

CO = """NumFac: 323200000129
FecFac: 2019-01-16
HorFac: 10:53:10-05:00
NitFac: 700085371
DocAdq: 800199436
ValFac: 1500000.00
ValIva: 285000.00
ValOtroIm: 0.00
ValTolFac: 1785000.00
CUFE: e5bac48e354bc907bccff0ea7d45fbf784f0a8e7243b58337361e1fbd430489d
https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey=e5bac48e354bc907bccff0ea7d45fbf784f0a8e7243b58337361e1fbd430489d"""


def test_co_ejemplo_del_anexo_tecnico():
    r = co_dian.parse_co_dian(CO)
    assert r.warnings == []
    assert r.headline == ("Importe", "$ 1.785.000,00")
    assert r.subtitle == "Factura electrónica de venta · 323200000129 · 16/01/2019"
    d = items(r)
    assert d["NIT facturador"] == "700.085.371-1"
    assert d["Documento adquirente"] == "800199436"
    assert d["CUFE"].startswith("e5bac48e") and d["IVA"] == "$ 285.000,00"
    assert acciones(r)["Verificar en la DIAN ↗"].startswith("https://catalogo-vpfe.dian.gov.co/document/searchqr?")


def test_co_solo_url():
    r = co_dian.parse_co_dian(CO.splitlines()[-1])
    assert r.warnings == [] and items(r)["CUFE"].startswith("e5bac48e")


def test_co_nit_alterado():
    r = co_dian.parse_co_dian(CO.replace("NitFac: 700085371", "NitFac: 70008537X"))
    assert any("NIT del facturador" in w for w in r.warnings)


def test_co_cufe_distinto_del_enlace():
    r = co_dian.parse_co_dian(CO.replace("CUFE: e5bac48e", "CUFE: f5bac48e"))
    assert any("no coincide" in w for w in r.warnings)


def test_co_qr_roto():
    r = co_dian.parse_co_dian("NumFac: 323200000129\nNitFac: 700085371\nValTolFac: mucho")
    assert AVISO_INCOMPLETO in r.warnings


def test_co_texto_ajeno():
    assert co_dian.parse_co_dian("Factura número 12") is None


# ---------------------------------------------------------------- Uruguay: DGI

UY = "https://www.efactura.dgi.gub.uy/consultaQR/cfe?219999990016,111,A,1234,1220.00,21/10/2026,Ab3dEf7hIj+/kLm="


def test_uy_efactura():
    r = uy_dgi.parse_uy_dgi(UY)
    assert r.warnings == []
    assert r.headline == ("Importe", "$ 1.220,00")
    assert r.subtitle == "e-Factura · A 1234 · 21/10/2026"
    d = items(r)
    assert d["RUC emisor"] == "219999990016" and d["Código de seguridad"] == "Ab3dEf7hIj+/kLm="
    assert acciones(r)["Verificar en DGI ↗"] == UY


def test_uy_contingencia():
    assert uy_dgi.parse_uy_dgi(UY.replace(",111,", ",211,")).subtitle.startswith("e-Factura (contingencia)")


def test_uy_ruc_alterado():
    r = uy_dgi.parse_uy_dgi(UY.replace("219999990016", "219999990017"))
    assert any("RUC del emisor" in w for w in r.warnings)


def test_uy_qr_roto():
    r = uy_dgi.parse_uy_dgi("https://www.efactura.dgi.gub.uy/consultaQR/cfe?219999990016,111")
    assert AVISO_INCOMPLETO in r.warnings


def test_uy_texto_ajeno():
    assert uy_dgi.parse_uy_dgi("https://www.dgi.gub.uy/") is None


# ---------------------------------------------------------------- Brasil: NFC-e / NF-e

CHAVE = "43150108287693000157651010000000971000001251"  # ejemplo de la NT 2025.001
BR = f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p={CHAVE}|2|1|1|ecc4f0e7e612456f2e3521768bd572b6f0eae240"


def test_br_nfce_v2_en_linea():
    r = br_nfe.parse_br_nfe(BR)
    assert r.warnings == []
    assert r.headline == ("NFC-e", "000.000.097")  # el QR en línea no lleva el importe
    d = items(r)
    assert d["CNPJ emisor"] == "08.287.693/0001-57"
    assert d["Serie"] == "101" and d["Estado"] == "RS" and d["Mes de emisión"] == "01/2015"
    assert d["Clave de acceso"].startswith("4315 0108 2876")
    a = acciones(r)
    assert a["Verificar en la SEFAZ-RS ↗"] == BR and a["Copiar clave"] == CHAVE


def test_br_nfce_contingencia_con_valor():
    url = f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p={CHAVE}|2|1|20|1.00|6c3765|1|abcdef"
    r = br_nfe.parse_br_nfe(url)
    assert r.headline == ("Importe", "R$ 1,00")
    assert r.subtitle == "NFC-e · 000.000.097 · 20/01/2015"


def test_br_nfce_v3_homologacion():
    r = br_nfe.parse_br_nfe(f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p={CHAVE}|3|2")
    assert any("homologación" in w for w in r.warnings)


def test_br_nfce_v1():
    r = br_nfe.parse_br_nfe(f"https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?chNFe={CHAVE}&nVersao=100&tpAmb=1"
                            "&vNF=1.00&cHashQRCode=ecc4")
    assert r.headline == ("Importe", "R$ 1,00")


def test_br_clave_sola():
    r = br_nfe.parse_br_nfe(CHAVE)
    assert r is not None and items(r)["CNPJ emisor"] == "08.287.693/0001-57"
    assert r.actions[0][0] == "Copiar clave"  # sin URL no hay botón de verificar


def test_br_clave_alterada():
    alterada = CHAVE[:10] + "4" + CHAVE[11:]  # cambia una cifra del CNPJ
    r = br_nfe.parse_br_nfe(BR.replace(CHAVE, alterada))
    assert any("dígito verificador" in w for w in r.warnings)
    assert any("CNPJ del emisor" in w for w in r.warnings)
    assert br_nfe.parse_br_nfe(alterada) is None  # la clave sola solo se reconoce si cuadra


def test_br_qr_roto():
    r = br_nfe.parse_br_nfe("https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=4315010828769300015765|2")
    assert AVISO_INCOMPLETO in r.warnings


def test_br_texto_ajeno():
    assert br_nfe.parse_br_nfe("https://www.gov.br/receitafederal") is None
    assert br_nfe.parse_br_nfe("1" * 44) is None


# ---------------------------------------------------------------- Ecuador: SRI

EC = "2110201101179214673900110020010000000011234567813"  # ejemplo de la ficha técnica del SRI


def test_ec_clave_de_acceso():
    r = ec_sri.parse_ec_sri(EC)
    assert r.warnings == ["Comprobante del ambiente de pruebas: sin validez tributaria"]  # el ejemplo es de pruebas
    assert r.headline == ("Factura", "002-001-000000001")  # la clave no lleva importe
    assert r.subtitle == "Factura · 002-001-000000001 · 21/10/2011"
    d = items(r)
    assert d["RUC emisor"] == "1792146739001" and d["Clave de acceso"] == EC
    assert d["Ambiente"] == "Pruebas"
    a = acciones(r)
    assert a["Copiar clave"] == EC and a["Verificar en el SRI ↗"] == ec_sri.URL_SRI


def test_ec_ruc_que_no_verifica():
    clave = EC[:10] + "1792146738001" + EC[23:48]
    clave += str(ec_sri.clave_dv(clave))
    r = ec_sri.parse_ec_sri(clave)
    assert any("RUC del emisor" in w for w in r.warnings)


def test_ec_ambiente_de_produccion():
    clave = EC[:23] + "2" + EC[24:48]
    clave += str(ec_sri.clave_dv(clave))
    r = ec_sri.parse_ec_sri(clave)
    assert r.warnings == [] and items(r)["Ambiente"] == "Producción"


def test_ec_solo_si_cuadra_el_digito():
    assert ec_sri.parse_ec_sri(EC[:48] + "4") is None
    assert ec_sri.parse_ec_sri("1" * 49) is None
    assert ec_sri.parse_ec_sri("hola") is None


# ---------------------------------------------------------------- integración con analyze()

@pytest.mark.parametrize("texto, sistema", [
    (MX, "SAT (CFDI)"), (CL, "SII (DTE)"), (PE, "SUNAT"), (CO, "DIAN"), (UY, "DGI (CFE)"),
    (BR, "SEFAZ-RS"), (CHAVE, "SEFAZ-RS"), (EC, "SRI"),
])
def test_analyze_reconoce_cada_pais(texto, sistema):
    r = analyze(texto)
    assert r.kind == "invoice" and r.title.endswith(sistema)


def test_formatos_rotos_no_lanzan_excepciones():
    for parse in (mx_cfdi.parse_mx_cfdi, cl_sii.parse_cl_sii, pe_sunat.parse_pe_sunat, co_dian.parse_co_dian,
                  uy_dgi.parse_uy_dgi, br_nfe.parse_br_nfe, ec_sri.parse_ec_sri):
        for texto in ("", "|||", "<TED><DD>", "NumFac:", "https://www.efactura.dgi.gub.uy/consultaQR/cfe?",
                      "https://x.gov.br/?p=|||", "?re=", "00000000000|00|0000|"):
            parse(texto)
