"""Documentos personales: DNI argentino (PDF417 del frente) y tarjetas de embarque IATA (BCBP).

Son datos personales: el Result va con private=True y no se guarda en el historial.
"""
import re
from datetime import date, timedelta

from clipqr.structured import Result, register

PRIVATE_NOTE = "Datos personales: no se guardan en el historial"
SEX = {"M": "Masculino", "F": "Femenino", "X": "No binario"}


def _dni(number):
    d = re.sub(r"\D", "", number)
    return f"{int(d):,}".replace(",", ".") if d else number.strip()


def _date(text):
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", text.strip())
    return f"{m[1]}/{m[2]}/{m[3]}" if m else ""


def _identity(nombre, apellido, dni, sexo, nacimiento, emision, ejemplar, tramite):
    full = " ".join(x.strip().title() for x in (nombre, apellido) if x.strip())
    items = [("DNI", _dni(dni)), ("Apellido", apellido.strip().title()), ("Nombre", nombre.strip().title()),
             ("Sexo", SEX.get(sexo.strip().upper(), sexo.strip())), ("Nacimiento", _date(nacimiento)),
             ("Emisión", _date(emision)), ("Ejemplar", ejemplar.strip()), ("Número de trámite", tramite.strip())]
    items = [i for i in items if i[1]]
    actions = [("Copiar DNI", "copy", re.sub(r"\D", "", dni)), ("Copiar nombre completo", "copy", full)]
    return Result("identity", "DNI · Argentina", items, actions, [], ("Titular", full or _dni(dni)),
                  PRIVATE_NOTE, private=True)


@register
def parse_dni_ar(text):
    """PDF417 del DNI argentino. Formato actual (desde 2012):
    trámite@APELLIDO@NOMBRE@SEXO@DNI@EJEMPLAR@NACIMIENTO@EMISIÓN@CUIL…
    Formato anterior (empieza con «@»): @DNI@EJEMPLAR@…@APELLIDO@NOMBRE@NACIONALIDAD@NACIMIENTO@SEXO@EMISIÓN@TRÁMITE@…"""
    t = text.strip()
    f = t.split("@")
    if len(f) >= 8 and re.fullmatch(r"\d{8,15}", f[0]) and f[3].strip() in SEX \
            and re.fullmatch(r"\d{7,8}", f[4].strip()) and _date(f[6]):
        return _identity(f[2], f[1], f[4], f[3], f[6], f[7], f[5], f[0])
    if t.startswith("@") and len(f) >= 11 and re.fullmatch(r"\d{7,8}", f[1].strip()) \
            and f[8].strip() in SEX and _date(f[7]):
        # TODO verificar con DNI reales: el formato anterior a 2012 tiene variantes según la planta emisora
        return _identity(f[5], f[4], f[1], f[8], f[7], f[9], f[2], f[10])
    return None


# ---------------------------------------------------------------- tarjeta de embarque (IATA BCBP)

COMPARTMENTS = {"F": "Primera", "A": "Primera", "J": "Business", "C": "Business", "D": "Business",
                "W": "Turista premium", "Y": "Turista", "B": "Turista", "M": "Turista", "H": "Turista"}


def julian_to_date(day, today=None):
    """Día del año de la tarjeta (sin año) -> la fecha más cercana a hoy (vuelos de ayer o del año que viene)."""
    today = today or date.today()
    candidates = []
    for year in (today.year - 1, today.year, today.year + 1):
        try:
            candidates.append(date(year, 1, 1) + timedelta(days=day - 1))
        except OverflowError:
            pass
    candidates = [d for d in candidates if d.timetuple().tm_yday == day]
    return min(candidates, key=lambda d: abs((d - today).days)) if candidates else None


@register
def parse_bcbp(text, today=None):
    """Tarjeta de embarque IATA Resolución 792 (código PDF417, Aztec o QR que empieza por «M1»…)."""
    t = text.rstrip("\r\n")
    if not re.match(r"^M[1-4].{20}[ E]", t) or len(t) < 60:
        return None
    name = t[2:22].strip()
    pnr, origin, dest = t[23:30].strip(), t[30:33].strip(), t[33:36].strip()
    carrier, flight = t[36:39].strip(), t[39:44].strip().lstrip("0")
    julian, compartment, seat, seq = t[44:47].strip(), t[47], t[48:52].strip(), t[52:57].strip()
    if not (re.fullmatch(r"[A-Z]{3}", origin) and re.fullmatch(r"[A-Z]{3}", dest)
            and re.fullmatch(r"[A-Z0-9]{2,3}", carrier)):
        return None
    when = julian_to_date(int(julian), today) if julian.isdigit() and 1 <= int(julian) <= 366 else None
    surname, _, given = name.partition("/")
    passenger = " ".join(x.title() for x in (given, surname) if x) or name
    flight_no = f"{carrier} {flight}"
    items = [("Pasajero", passenger), ("Vuelo", flight_no), ("Origen", origin), ("Destino", dest)]
    if when:
        items.append(("Fecha", when.strftime("%d/%m/%Y")))
    seat_shown = seat.lstrip("0")
    if seat_shown:
        items.append(("Asiento", seat_shown))
    items.append(("Reserva", pnr))
    if compartment.strip():
        items.append(("Clase", COMPARTMENTS.get(compartment, compartment)))
    if seq.lstrip("0"):
        items.append(("Secuencia", seq.lstrip("0")))
    if t[1] != "1":
        items.append(("Tramos", t[1]))
    subtitle = f"{origin} → {dest}" + (f" · {when:%d/%m/%Y}" if when else "") + " · no va al historial"
    actions = [("Copiar reserva", "copy", pnr),
               ("Estado del vuelo ↗", "open", f"https://www.google.com/search?q={carrier}{flight}")]
    return Result("boarding", "Tarjeta de embarque", items, actions, [], ("Vuelo", flight_no), subtitle,
                  private=True)
