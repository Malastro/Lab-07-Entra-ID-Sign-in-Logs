
import pandas as pd
import unicodedata
import re
from pathlib import Path

# ============================================================
# CONFIGURACION
# ============================================================

BASE_DIR = Path(__file__).parent

SIGNINS_FILE = BASE_DIR / "InteractiveSignIns_2026-11-01_2026-11-02.csv"
AUTH_FILE = BASE_DIR / "InteractiveSignIns_AuthDetails_2026-11-01_2026-11-02.csv"
REPORT_FILE = BASE_DIR / "T05_search_results.txt"


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
# CARGA DE ARCHIVOS
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
            "Fecha UTC", "Fecha y hora UTC", "Fecha",
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
            "Estado de Acceso Condicional",
            "Conditional Access status",
            "Resultado de Acceso Condicional"
        ]),
        "user": find_column(signins, [
            "Nombre principal de usuario",
            "User principal name",
            "UPN",
            "Usuario"
        ]),
        "request": find_column(signins, [
            "Id. de solicitud", "Request ID", "Request Id"
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
            "Navegador", "Browser"
        ]),
        "os": find_column(signins, [
            "Sistema operativo", "Operating system"
        ]),
        "managed": find_column(signins, [
            "Dispositivo administrado", "Managed"
        ]),
        "compliant": find_column(signins, [
            "Dispositivo compatible", "Compliant"
        ]),
        "ca_policies": find_column(signins, [
            "Políticas de acceso condicional",
            "Conditional Access policies"
        ])
    }

    columns["auth_request"] = find_column(auth, [
        "Id. de solicitud", "Request ID", "Request Id"
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

    return columns


# ============================================================
# INFORME
# ============================================================

report_lines = []


def output(text=""):
    print(text)
    report_lines.append(str(text))


def show_authentication_details(row, request_id, auth, columns):

    output("\n  AUTHENTICATION DETAILS")
    output("  " + "-" * 55)

    auth_request = columns["auth_request"]

    if not request_id or not auth_request:
        output("  No se puede realizar la correlación.")
        return

    matches = auth[
        auth[auth_request].astype(str).str.strip() == request_id
    ]

    if matches.empty:
        output("  No se encontraron detalles asociados.")
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


def show_event(row, index, auth, columns):

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

    # No imprimimos UPN, IP ni identificadores.
    request_id = get_value(row, columns["request"])

    show_authentication_details(
        row, request_id, auth, columns
    )


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
        show_event(row, number, auth, columns)


def show_all_events(signins, auth, columns):

    results = signins.copy()

    if columns["date"]:
        results = results.sort_values(
            by=columns["date"],
            ascending=False,
            na_position="last"
        )

    output(f"\nTotal de eventos: {len(results)}")

    for number, (_, row) in enumerate(results.iterrows(), 1):
        show_event(row, number, auth, columns)


def search_by_user(signins, auth, columns):

    user_col = columns["user"]

    if not user_col:
        output("No se ha identificado la columna de usuario.")
        output("Columnas disponibles:")
        for col in signins.columns:
            output(f"  {col}")
        return

    user = input("\nIntroduce el UPN o nombre de usuario: ").strip()

    results = signins[
        signins[user_col].astype(str).str.contains(
            user, case=False, na=False, regex=False
        )
    ]

    output(f"\nEventos encontrados: {len(results)}")

    for number, (_, row) in enumerate(results.iterrows(), 1):
        show_event(row, number, auth, columns)


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
