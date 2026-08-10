from datetime import date, datetime


def fecha_cumpleanos_anio_actual(fecha_nacimiento):
    if not fecha_nacimiento:
        return None
    year_actual = date.today().year
    try:
        return date(year_actual, fecha_nacimiento.month, fecha_nacimiento.day)
    except ValueError:
        # Feb 29 in non-leap year
        return date(year_actual, fecha_nacimiento.month, 28)


def format_fecha(d, fmt="%d/%m/%Y"):
    if isinstance(d, (date, datetime)):
        return d.strftime(fmt)
    return str(d) if d else ""


def parse_fecha(s, fmt="%Y-%m-%d"):
    if not s:
        return None
    try:
        return datetime.strptime(str(s).strip(), fmt).date()
    except ValueError:
        return None
