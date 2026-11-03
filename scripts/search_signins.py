import pandas as pd
import unicodedata
import re
from pathlib import Path

# ============================================================
# CONFIGURACION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR.parent
DATA_DIR = REPO_DIR / "data"
REPORTS_DIR = REPO_DIR / "reports"

def resolve_file(filename):
    # Busca primero en data/, luego en scripts/, y luego en el directorio actual
    for candidate in [DATA_DIR / filename, BASE_DIR / filename, Path.cwd() / "data" / filename, Path.cwd() / filename]:
        if candidate.exists():
            return candidate
    return DATA_DIR / filename

SIGNINS_FILE = resolve_file("InteractiveSignIns_2026-11-01_2026-11-02.csv")
AUTH_FILE = resolve_file("InteractiveSignIns_AuthDetails_2026-11-01_2026-11-02.csv")

if not REPORTS_DIR.exists():
    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

REPORT_FILE = (REPORTS_DIR if REPORTS_DIR.exists() else BASE_DIR) / "T05_search_results.txt"


# ============================================================
# UTILIDADES
# ============================================================

def normalize(value):
    value = str(value).replace("\ufeff", "").replace('"', "").strip().lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", value)


def clean(value):
    if pd.isna(value) or str(value).strip().lower() in ("nan", "none", ""):
        return "No disponible"
    return str(value).strip()


def find_column(df, aliases):
    columns = {normalize(col): col for col in df.columns}

    # Primero buscamos coincidencia exacta
    for alias in aliases:
        key = normalize(alias)
        if key in columns:
            return columns[key]

    # Después buscamos coincidencias parciales
    for alias in aliases:
        key = normalize(alias)
        if len(key) >= 5:
            for normalized_col, original_col in columns.items():
                if key in normalized_col:
                    return original_col

    return None


def get_value(row, column):
    if column is None:
        return "No disponible"
    return clean(row.get(column))


# ============================================================
# CARGA DE ARCHIVOS Y NORMALIZACION
# ============================================================

def load_data():
    if not SIGNINS_FILE.exists():
        raise FileNotFoundError(f"No encuentro: {SIGNINS_FILE.name}")

    if not AUTH_FILE.exists():
        raise FileNotFoundError(f"No encuentro: {AUTH_FILE.name}")

    signins = pd.read_csv(
        SIGNINS_FILE,
        sep=None,
        engine="python",
        dtype=str,
        encoding="utf-8-sig"
    )

    auth = pd.read_csv(
        AUTH_FILE,
        sep=None,
        engine="python",
        dtype=str,
        encoding="utf-8-sig"
    )

    return signins, auth


# ============================================================
# IDENTIFICACION DE COLUMNAS
# ============================================================

def identify_columns(signins, auth):

    columns = {
        "error": find_column(signins, [
            "Código de error", "Sign-in error code", "Error code"
        ]),
        "date": find_column(signins, [
            "Fecha UTC", "Fecha y hora UTC", "Fecha (UTC)", "Fecha",
            "Date", "Created date time", "CreatedDateTime"
        ]),
        "status": find_column(signins, [
            "Estado", "Status"
        ]),
        "reason": find_column(signins, [
            "Motivo del error", "Failure reason"
        ]),
        "application": find_column(signins, [
            "Aplicación", "Application"
        ]),
        "resource": find_column(signins, [
            "Recurso", "Resource"
        ]),
        "requirement": find_column(signins, [
            "Requisito de autenticación", "Authentication requirement"
        ]),
        "ca_status": find_column(signins, [
            "Acceso condicional",
            "Estado de Acceso Condicional",
            "Conditional Access status",
            "Resultado de Acceso Condicional"
        ]),
        "user": find_column(signins, [
            "Nombre principal de usuario",
            "User principal name",
            "UPN",
            "Usuario",
            "Nombre de usuario"
        ]),
        "ip": find_column(signins, [
            "Dirección IP", "IP address"
        ]),
        "location": find_column(signins, [
            "Ubicación", "Location"
        ]),
        "client": find_column(signins, [
            "Aplicación cliente", "Client app"
        ]),
        "browser": find_column(signins, [
            "Navegador", "Browser", "Explorador"
        ]),
        "os": find_column(signins, [
            "Sistema operativo", "Operating system"
        ]),
        "managed": find_column(signins, [
            "Dispositivo administrado", "Managed", "Administrada"
        ]),
        "compliant": find_column(signins, [
            "Dispositivo compatible", "Compliant", "Conforme"
        ]),
        "ca_policies": find_column(signins, [
            "Políticas de acceso condicional",
            "Conditional Access policies"
        ])
    }

    # Columnas de Authentication Details
    columns["auth_date"] = find_column(auth, [
        "Fecha", "Fecha UTC", "Fecha y hora UTC", "Fecha (UTC)",
        "Date", "Created date time", "CreatedDateTime"
    ])

    columns["auth_method"] = find_column(auth, [
        "Método de autenticación", "Authentication method"
    ])

    columns["auth_method_detail"] = find_column(auth, [
        "Detalle del método de autenticación",
        "Authentication method detail"
    ])

    columns["auth_succeeded"] = find_column(auth, [
        "Correcto", "Succeeded"
    ])

    columns["auth_result"] = find_column(auth, [
        "Detalle del resultado", "Result detail"
    ])

    # Normalización de marcas temporales a UTC mediante Pandas
    if columns["date"]:
        signins["_parsed_datetime"] = pd.to_datetime(
            signins[columns["date"]], utc=True, errors="coerce"
        )
    else:
        signins["_parsed_datetime"] = pd.NaT

    if columns["auth_date"]:
        auth["_parsed_datetime"] = pd.to_datetime(
            auth[columns["auth_date"]], utc=True, errors="coerce"
        )
    else:
        auth["_parsed_datetime"] = pd.NaT

    return columns


# ============================================================
# INFORME
# ============================================================

report_lines = []


def output(text=""):
    print(text)
    report_lines.append(str(text))


def show_authentication_details(row, auth, columns, signins):

    output("\n  AUTHENTICATION DETAILS")
    output("  " + "-" * 55)
    output("  Aviso: Asociación basada en marca temporal UTC (sin identificador único).")

    event_dt = row.get("_parsed_datetime")
    raw_date = get_value(row, columns["date"])

    # Tratamiento de fechas inválidas o no disponibles
    if pd.isna(event_dt):
        output(f"  [ERROR] Fecha no válida o no disponible ('{raw_date}'). No se puede asociar.")
        return

    # Control de ambigüedades: detectar colisiones temporales en Sign-in Logs
    if "_parsed_datetime" in signins.columns:
        same_dt_count = (signins["_parsed_datetime"] == event_dt).sum()
        if same_dt_count > 1:
            output(f"  [ADVERTENCIA] Múltiples eventos de inicio ({same_dt_count}) comparten el timestamp exacto ({event_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}).")
            output("  Asociación automática bloqueada para evitar datos ambiguos.")
            return

    # Comprobar que auth cuenta con marcas temporales normalizadas
    if "_parsed_datetime" not in auth.columns or columns["auth_date"] is None:
        output("  [ERROR] No se identificó la columna de fecha en Authentication Details.")
        return

    # Asociación por igualdad exacta de timestamp UTC
    matches = auth[auth["_parsed_datetime"] == event_dt]

    if matches.empty:
        output(f"  No se encontraron detalles asociados para esta marca temporal ({raw_date}).")
        return

    for number, (_, auth_row) in enumerate(matches.iterrows(), 1):
        output(f"\n  Paso de autenticación {number}")

        fields = [
            ("Método", "auth_method"),
            ("Detalle del método", "auth_method_detail"),
            ("Correcto", "auth_succeeded"),
            ("Resultado", "auth_result")
        ]

        for label, key in fields:
            output(f"    {label}: {get_value(auth_row, columns[key])}")


def show_event(row, index, auth, columns, signins):

    output("\n" + "=" * 70)
    output(f"EVENTO #{index}")
    output("=" * 70)

    fields = [
        ("Fecha", "date"),
        ("Estado", "status"),
        ("Código de error", "error"),
        ("Motivo del error", "reason"),
        ("Aplicación", "application"),
        ("Recurso", "resource"),
        ("Requisito de autenticación", "requirement"),
        ("Conditional Access", "ca_status"),
        ("Políticas CA", "ca_policies"),
        ("Aplicación cliente", "client"),
        ("Navegador", "browser"),
        ("Sistema operativo", "os"),
        ("Dispositivo administrado", "managed"),
        ("Dispositivo compatible", "compliant")
    ]

    for label, key in fields:
        value = get_value(row, columns[key])
        if value != "No disponible":
            output(f"{label}: {value}")

    show_authentication_details(row, auth, columns, signins)


# ============================================================
# BUSQUEDAS
# ============================================================

def search_by_error(signins, auth, columns):

    if not columns["error"]:
        output("No se reconoce la columna de código de error.")
        return

    code = input("\nIntroduce el código de error: ").strip()

    results = signins[
        signins[columns["error"]].astype(str).str.strip() == code
    ]

    output(f"\nEventos encontrados: {len(results)}")

    for number, (_, row) in enumerate(results.iterrows(), 1):
        show_event(row, number, auth, columns, signins)


def show_all_events(signins, auth, columns):

    results = results.sort_values(
    by="_parsed_datetime",
    ascending=False,
    na_position="last"
)

    output(f"\nTotal de eventos: {len(results)}")

    for number, (_, row) in enumerate(results.iterrows(), 1):
        show_event(row, number, auth, columns, signins)


def search_by_user(signins, auth, columns):

    user_col = columns["user"]

    if not user_col:
        output("No se ha identificado la columna de usuario.")
        output("Columnas disponibles:")
        for col in signins.columns:
            output(f"  {col}")
        return

    user = input("\nIntroduce el UPN o nombre de usuario: ").strip()

    mask = signins[user_col].astype(str).str.contains(
        user, case=False, na=False, regex=False
    )
    for alt_col in ["Usuario", "Nombre de usuario", "Nombre principal de usuario"]:
        if alt_col in signins.columns and alt_col != user_col:
            mask = mask | signins[alt_col].astype(str).str.contains(
                user, case=False, na=False, regex=False
            )

    results = signins[mask]

    output(f"\nEventos encontrados: {len(results)}")

    for number, (_, row) in enumerate(results.iterrows(), 1):
        show_event(row, number, auth, columns, signins)


# ============================================================
# MENU PRINCIPAL
# ============================================================

def main():

    try:
        signins, auth = load_data()
        columns = identify_columns(signins, auth)

    except Exception as error:
        print(f"\nERROR: {error}")
        return

    print("\n" + "=" * 55)
    print("       IAM - SIGN-IN LOGS INVESTIGATION TOOL")
    print("=" * 55)

    print(f"Sign-in Logs: {len(signins)} registros")
    print(f"Authentication Details: {len(auth)} registros")

    print("\n1. Buscar por código de error")
    print("2. Mostrar todos los eventos")
    print("3. Buscar por usuario")
    print("0. Salir")

    option = input("\nSelecciona una opción: ").strip()

    if option == "1":
        search_by_error(signins, auth, columns)

    elif option == "2":
        show_all_events(signins, auth, columns)

    elif option == "3":
        search_by_user(signins, auth, columns)

    elif option == "0":
        print("Saliendo...")
        return

    else:
        print("Opción no válida.")
        return

    # Guardar informe
    REPORT_FILE.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    print("\n" + "=" * 55)
    print(f"Informe guardado: {REPORT_FILE.name}")
    print("=" * 55)


if __name__ == "__main__":
    main()
