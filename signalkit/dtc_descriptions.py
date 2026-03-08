# =============================================================================
# dtc_descriptions.py - OBD2 Diagnostic Trouble Code Descriptions
# =============================================================================
# Maps standard OBD2 DTC codes to plain-English descriptions.
# Covers P (Powertrain), B (Body), C (Chassis), and U (Network) codes.
#
# This is not exhaustive — it covers the most common codes. If a code is not
# found here, get_dtc_description() will return a generic fallback message.
# =============================================================================

# Standard OBD2 DTC code descriptions
DTC_CODES = {
    # -------------------------------------------------------------------------
    # P0xxx - Powertrain: Generic OBD2 codes
    # -------------------------------------------------------------------------

    # Fuel and Air Metering
    "P0100": "Mass Air Flow (MAF) sensor circuit malfunction",
    "P0101": "MAF sensor circuit range/performance",
    "P0102": "MAF sensor circuit low input",
    "P0103": "MAF sensor circuit high input",
    "P0104": "MAF sensor circuit intermittent",
    "P0105": "Manifold Absolute Pressure (MAP) sensor circuit malfunction",
    "P0106": "MAP sensor circuit range/performance",
    "P0107": "MAP sensor circuit low input",
    "P0108": "MAP sensor circuit high input",
    "P0109": "MAP sensor circuit intermittent",
    "P0110": "Intake Air Temperature (IAT) sensor circuit malfunction",
    "P0111": "IAT sensor circuit range/performance",
    "P0112": "IAT sensor circuit low input",
    "P0113": "IAT sensor circuit high input",
    "P0114": "IAT sensor circuit intermittent",
    "P0115": "Engine Coolant Temperature (ECT) sensor circuit malfunction",
    "P0116": "ECT sensor circuit range/performance",
    "P0117": "ECT sensor circuit low input (shorted to ground)",
    "P0118": "ECT sensor circuit high input (open circuit)",
    "P0119": "ECT sensor circuit intermittent",
    "P0120": "Throttle Position (TPS) sensor circuit malfunction",
    "P0121": "TPS sensor circuit range/performance",
    "P0122": "TPS sensor circuit low input",
    "P0123": "TPS sensor circuit high input",
    "P0124": "TPS sensor circuit intermittent",
    "P0125": "Insufficient coolant temperature for closed-loop fuel control",
    "P0126": "Insufficient coolant temperature for stable operation",

    # Oxygen Sensors
    "P0130": "O2 sensor circuit malfunction (Bank 1, Sensor 1)",
    "P0131": "O2 sensor circuit low voltage (Bank 1, Sensor 1)",
    "P0132": "O2 sensor circuit high voltage (Bank 1, Sensor 1)",
    "P0133": "O2 sensor circuit slow response (Bank 1, Sensor 1)",
    "P0134": "O2 sensor circuit no activity detected (Bank 1, Sensor 1)",
    "P0135": "O2 sensor heater circuit malfunction (Bank 1, Sensor 1)",
    "P0136": "O2 sensor circuit malfunction (Bank 1, Sensor 2)",
    "P0137": "O2 sensor circuit low voltage (Bank 1, Sensor 2)",
    "P0138": "O2 sensor circuit high voltage (Bank 1, Sensor 2)",
    "P0139": "O2 sensor circuit slow response (Bank 1, Sensor 2)",
    "P0140": "O2 sensor circuit no activity detected (Bank 1, Sensor 2)",
    "P0141": "O2 sensor heater circuit malfunction (Bank 1, Sensor 2)",
    "P0150": "O2 sensor circuit malfunction (Bank 2, Sensor 1)",
    "P0151": "O2 sensor circuit low voltage (Bank 2, Sensor 1)",
    "P0152": "O2 sensor circuit high voltage (Bank 2, Sensor 1)",
    "P0153": "O2 sensor circuit slow response (Bank 2, Sensor 1)",
    "P0154": "O2 sensor circuit no activity detected (Bank 2, Sensor 1)",
    "P0155": "O2 sensor heater circuit malfunction (Bank 2, Sensor 1)",
    "P0160": "O2 sensor circuit malfunction (Bank 2, Sensor 2)",
    "P0161": "O2 sensor heater circuit malfunction (Bank 2, Sensor 2)",

    # Fuel System
    "P0170": "Fuel trim malfunction (Bank 1)",
    "P0171": "System too lean (Bank 1) — possible vacuum leak or weak fuel pump",
    "P0172": "System too rich (Bank 1) — possible injector leak or high fuel pressure",
    "P0173": "Fuel trim malfunction (Bank 2)",
    "P0174": "System too lean (Bank 2)",
    "P0175": "System too rich (Bank 2)",

    # Misfire
    "P0300": "Random/multiple cylinder misfire detected",
    "P0301": "Cylinder 1 misfire detected",
    "P0302": "Cylinder 2 misfire detected",
    "P0303": "Cylinder 3 misfire detected",
    "P0304": "Cylinder 4 misfire detected",
    "P0305": "Cylinder 5 misfire detected",
    "P0306": "Cylinder 6 misfire detected",
    "P0307": "Cylinder 7 misfire detected",
    "P0308": "Cylinder 8 misfire detected",

    # Knock Sensor
    "P0325": "Knock sensor 1 circuit malfunction (Bank 1)",
    "P0326": "Knock sensor 1 circuit range/performance (Bank 1)",
    "P0327": "Knock sensor 1 circuit low input (Bank 1)",
    "P0328": "Knock sensor 1 circuit high input (Bank 1)",
    "P0330": "Knock sensor 2 circuit malfunction (Bank 2)",

    # Crankshaft/Camshaft Position
    "P0335": "Crankshaft position sensor A circuit malfunction",
    "P0336": "Crankshaft position sensor A circuit range/performance",
    "P0337": "Crankshaft position sensor A circuit low input",
    "P0338": "Crankshaft position sensor A circuit high input",
    "P0340": "Camshaft position sensor A circuit malfunction (Bank 1)",
    "P0341": "Camshaft position sensor A circuit range/performance (Bank 1)",
    "P0342": "Camshaft position sensor A circuit low input",
    "P0343": "Camshaft position sensor A circuit high input",
    "P0344": "Camshaft position sensor A circuit intermittent (Bank 1)",
    "P0345": "Camshaft position sensor A circuit malfunction (Bank 2)",

    # Ignition System
    "P0351": "Ignition coil A primary/secondary circuit malfunction",
    "P0352": "Ignition coil B primary/secondary circuit malfunction",
    "P0353": "Ignition coil C primary/secondary circuit malfunction",
    "P0354": "Ignition coil D primary/secondary circuit malfunction",
    "P0355": "Ignition coil E primary/secondary circuit malfunction",
    "P0356": "Ignition coil F primary/secondary circuit malfunction",

    # Catalyst
    "P0420": "Catalyst system efficiency below threshold (Bank 1) — likely bad catalytic converter",
    "P0421": "Warm-up catalyst efficiency below threshold (Bank 1)",
    "P0430": "Catalyst system efficiency below threshold (Bank 2)",
    "P0431": "Warm-up catalyst efficiency below threshold (Bank 2)",

    # EVAP System
    "P0440": "Evaporative emission control system malfunction",
    "P0441": "EVAP system incorrect purge flow",
    "P0442": "EVAP system small leak detected — check gas cap first",
    "P0443": "EVAP purge control valve circuit malfunction",
    "P0444": "EVAP purge control valve circuit open",
    "P0445": "EVAP purge control valve circuit shorted",
    "P0446": "EVAP system vent control circuit malfunction",
    "P0447": "EVAP system vent control circuit open",
    "P0448": "EVAP system vent control circuit shorted",
    "P0449": "EVAP system vent valve/solenoid circuit malfunction",
    "P0450": "EVAP system pressure sensor malfunction",
    "P0451": "EVAP system pressure sensor range/performance",
    "P0452": "EVAP system pressure sensor low input",
    "P0453": "EVAP system pressure sensor high input",
    "P0455": "EVAP system large leak detected — check gas cap",
    "P0456": "EVAP system very small leak detected",
    "P0457": "EVAP system leak detected — loose or missing gas cap",

    # EGR
    "P0400": "Exhaust Gas Recirculation (EGR) flow malfunction",
    "P0401": "EGR flow insufficient",
    "P0402": "EGR flow excessive",
    "P0403": "EGR circuit malfunction",
    "P0404": "EGR circuit range/performance",
    "P0405": "EGR sensor A circuit low",
    "P0406": "EGR sensor A circuit high",
    "P0407": "EGR sensor B circuit low",
    "P0408": "EGR sensor B circuit high",
    "P0409": "EGR sensor A circuit malfunction",

    # Speed Sensors
    "P0500": "Vehicle Speed Sensor (VSS) malfunction",
    "P0501": "VSS range/performance",
    "P0502": "VSS circuit low input",
    "P0503": "VSS circuit intermittent/erratic/high",

    # Idle Control
    "P0505": "Idle Air Control (IAC) system malfunction",
    "P0506": "Idle control system RPM lower than expected",
    "P0507": "Idle control system RPM higher than expected",

    # Barometric Pressure
    "P0560": "System voltage malfunction",
    "P0561": "System voltage unstable",
    "P0562": "System voltage low",
    "P0563": "System voltage high",

    # Transmission
    "P0700": "Transmission control system malfunction",
    "P0705": "Transmission range sensor circuit malfunction",
    "P0710": "Transmission fluid temperature sensor circuit malfunction",
    "P0715": "Input/turbine speed sensor circuit malfunction",
    "P0720": "Output speed sensor circuit malfunction",
    "P0730": "Incorrect gear ratio",
    "P0740": "Torque converter clutch circuit malfunction",
    "P0750": "Shift solenoid A malfunction",
    "P0755": "Shift solenoid B malfunction",
    "P0760": "Shift solenoid C malfunction",
    "P0765": "Shift solenoid D malfunction",

    # Variable Valve Timing
    "P0010": "Camshaft position actuator circuit (Bank 1)",
    "P0011": "Camshaft position timing over-advanced (Bank 1)",
    "P0012": "Camshaft position timing over-retarded (Bank 1)",
    "P0013": "Camshaft position actuator circuit (Bank 1, exhaust)",
    "P0014": "Camshaft position timing over-advanced (Bank 1, exhaust)",
    "P0015": "Camshaft position timing over-retarded (Bank 1, exhaust)",
    "P0016": "Crankshaft/camshaft position correlation (Bank 1, sensor A)",
    "P0017": "Crankshaft/camshaft position correlation (Bank 1, sensor B)",
    "P0018": "Crankshaft/camshaft position correlation (Bank 2, sensor A)",
    "P0019": "Crankshaft/camshaft position correlation (Bank 2, sensor B)",
    "P0020": "Camshaft position actuator circuit (Bank 2)",
    "P0021": "Camshaft position timing over-advanced (Bank 2)",
    "P0022": "Camshaft position timing over-retarded (Bank 2)",

    # -------------------------------------------------------------------------
    # P1xxx - Powertrain: Manufacturer-specific codes (Kia/Hyundai)
    # -------------------------------------------------------------------------
    "P1166": "Air/fuel ratio control malfunction (Bank 1)",
    "P1167": "Air/fuel ratio control malfunction (Bank 2)",
    "P1250": "Pressure regulator control solenoid circuit",
    "P1308": "Crankshaft position sensor logical signal range",
    "P1326": "Knock sensor detection system",
    "P1505": "Idle air control valve opening coil malfunction",
    "P1506": "Idle air control valve closing coil malfunction",
    "P1529": "Vehicle speed sensor malfunction",
    "P1611": "MIL request circuit low voltage",
    "P1614": "MIL request circuit high voltage",
    "P1624": "MIL request signal from TCM",
    "P1633": "Sensor reference voltage B circuit",
    "P1693": "Turbocharger boost control solenoid",
    "P1695": "No CCD messages from body control module",

    # -------------------------------------------------------------------------
    # B0xxx - Body codes
    # -------------------------------------------------------------------------
    "B0001": "Driver airbag deployment control",
    "B0002": "Driver airbag deployment control 2nd stage",
    "B0010": "Passenger airbag deployment control",
    "B1000": "ECU malfunction (body control)",
    "B1001": "Option configuration error",

    # -------------------------------------------------------------------------
    # C0xxx - Chassis codes (ABS, stability control)
    # -------------------------------------------------------------------------
    "C0031": "Right front wheel speed sensor circuit",
    "C0034": "Right front wheel speed sensor circuit range/performance",
    "C0035": "Left front wheel speed sensor circuit",
    "C0036": "Left front wheel speed sensor circuit range/performance",
    "C0037": "Left rear wheel speed sensor circuit",
    "C0040": "Right rear wheel speed sensor circuit",
    "C0041": "Right rear wheel speed sensor circuit range/performance",
    "C0044": "Left rear wheel speed sensor circuit range/performance",
    "C0110": "ABS pump motor circuit malfunction",
    "C0121": "ABS valve relay circuit malfunction",
    "C0265": "ABS actuator relay circuit open",
    "C0266": "ABS actuator relay circuit shorted",

    # -------------------------------------------------------------------------
    # U0xxx - Network / Communication codes
    # -------------------------------------------------------------------------
    "U0001": "High speed CAN communication bus malfunction",
    "U0002": "High speed CAN communication bus performance",
    "U0100": "Lost communication with ECM/PCM",
    "U0101": "Lost communication with TCM",
    "U0121": "Lost communication with ABS control module",
    "U0140": "Lost communication with body control module",
    "U0155": "Lost communication with instrument panel cluster",
    "U0164": "Lost communication with HVAC control module",
}

# Kia Forte 1.8L specific known codes
KIA_FORTE_CODES = {
    "P1000": "OBD systems readiness test not complete — drive more to reset",
    "P1001": "Key-on engine-off test not complete",
    "P1260": "Theft detected — engine disabled",
    "P1345": "No SGC (CMP) signal to PCM",
    "P1386": "Knock sensor control zero test",
}

# Merge Kia-specific codes into main dict
DTC_CODES.update(KIA_FORTE_CODES)


def get_dtc_description(code: str) -> str:
    """
    Look up a plain-English description for an OBD2 DTC code.

    Args:
        code: DTC code string, e.g. "P0420" or "p0420" (case-insensitive)

    Returns:
        Human-readable description, or a generic fallback if code is unknown.
    """
    code = code.upper().strip()

    if code in DTC_CODES:
        return DTC_CODES[code]

    # Generate a category-based fallback description
    if len(code) >= 1:
        prefix = code[0]
        categories = {
            "P": "Powertrain",
            "B": "Body",
            "C": "Chassis",
            "U": "Network/Communication",
        }
        category = categories.get(prefix, "Unknown system")

        if len(code) >= 2:
            second = code[1]
            specificity = "generic OBD2" if second == "0" else "manufacturer-specific"
            return f"{category} fault — {specificity} code (no description available)"

    return f"Unknown fault code: {code}"


def format_dtc_list(codes: list) -> list:
    """
    Format a list of DTC codes into display-ready dicts.

    Args:
        codes: List of DTC code strings

    Returns:
        List of dicts with 'code' and 'description' keys
    """
    return [
        {"code": code, "description": get_dtc_description(code)}
        for code in codes
    ]
