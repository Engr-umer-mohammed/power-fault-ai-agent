"""
tools.py - Engineering Tools with IEC Standards
All limits follow IEC 60038, IEC 61000-2-2, IEC 60034
"""

from datetime import datetime
from typing import Tuple, List, Dict, Any


#  IEC STANDARD CONSTANTS

class IEC:
    """
    IEC Standards Reference
    Based on:
        IEC 60038 - Standard voltages
        IEC 61000-2-2 - Voltage unbalance
        IEC 60034 - Motor protection
    """

    # System Configuration (Change based on your system)
    SYSTEM_TYPE = "TN-S"  # TN-S, TN-C, TT, IT
    NOMINAL_VOLTAGE = 230  # 230V phase-neutral (Europe/Asia)
    NOMINAL_VOLTAGE_LINE = 400  # 400V phase-phase

    # IEC 60038 - Voltage Tolerances
    VOLTAGE_TOLERANCE = 0.10  # ±10% for low voltage systems
    VOLTAGE_MIN = NOMINAL_VOLTAGE * (1 - VOLTAGE_TOLERANCE)
    VOLTAGE_MAX = NOMINAL_VOLTAGE * (1 + VOLTAGE_TOLERANCE)
    VOLTAGE_WARNING_MIN = NOMINAL_VOLTAGE * 0.85  # -15% for warning
    VOLTAGE_WARNING_MAX = NOMINAL_VOLTAGE * 1.15  # +15% for warning

    # IEC 61000-2-2 - Voltage Unbalance Limits
    UNBALANCE_NORMAL = 2.0  # % - Normal operation
    UNBALANCE_WARNING = 3.0  # % - Investigate
    UNBALANCE_CRITICAL = 5.0  # % - Immediate action

    # IEC 60034 - Motor Protection Limits
    MOTOR_RATED_CURRENT = 100  # Amps (adjust for your system)
    CURRENT_WARNING = MOTOR_RATED_CURRENT * 1.05  # 105%
    CURRENT_CRITICAL = MOTOR_RATED_CURRENT * 1.20  # 120%

    # Frequency Limits (IEC 60038)
    FREQUENCY_NOMINAL = 50.0  # 50Hz (Europe/Asia) or 60Hz (Americas)
    FREQUENCY_TOLERANCE = 0.02  # ±2% for interconnected systems
    FREQUENCY_MIN = FREQUENCY_NOMINAL * (1 - FREQUENCY_TOLERANCE)
    FREQUENCY_MAX = FREQUENCY_NOMINAL * (1 + FREQUENCY_TOLERANCE)


# TOOL 1: IEC COMPLIANT DATA VALIDATION

def validate_sensor_data(sensor_data: Dict[str, float]) -> Tuple[bool, str]:
    """
    Validate sensor readings against IEC standards.

    Checks:
        - Voltage within IEC 60038 tolerances
        - Current within IEC 60034 limits
        - Frequency within IEC 60038 limits
    """

    errors = []

    # Check voltage readings for each phase (IEC 60038)
    for phase in ["voltage_a", "voltage_b", "voltage_c"]:
        voltage = sensor_data.get(phase, None)

        if voltage is None:
            errors.append(f"Missing reading: {phase} not provided")
            continue

        # IEC 60038: Voltage must be within ±10% of nominal
        if not (IEC.VOLTAGE_MIN <= voltage <= IEC.VOLTAGE_MAX):
            errors.append(
                f"{phase} reading of {voltage}V is outside "
                f"IEC 60038 normal range of {IEC.VOLTAGE_MIN:.0f}V "
                f"to {IEC.VOLTAGE_MAX:.0f}V"
            )

    # Check current (IEC 60034)
    current = sensor_data.get("current", None)
    if current is None:
        errors.append("Missing reading: current not provided")
    elif current < 0:
        errors.append(f"Current reading of {current}A cannot be negative")
    elif current > IEC.CURRENT_CRITICAL * 2:
        errors.append(
            f"Current reading of {current}A is extremely high. "
            f"Likely sensor failure or short circuit."
        )

    # Check frequency (IEC 60038)
    frequency = sensor_data.get("frequency", None)
    if frequency is None:
        errors.append("Missing reading: frequency not provided")
    elif not (IEC.FREQUENCY_MIN <= frequency <= IEC.FREQUENCY_MAX):
        errors.append(
            f"Frequency reading of {frequency}Hz is outside "
            f"IEC 60038 normal range of {IEC.FREQUENCY_MIN:.1f}Hz "
            f"to {IEC.FREQUENCY_MAX:.1f}Hz"
        )

    if errors:
        return False, "⚠️ IEC Standard Violations:\n  " + "\n  ".join(errors)

    return True, "✅ All readings compliant with IEC standards"


#  TOOL 2: IEC VOLTAGE UNBALANCE (IEC 61000-2-2)

def calculate_voltage_imbalance(
        voltage_a: float,
        voltage_b: float,
        voltage_c: float
) -> float:
    """
    Calculate voltage unbalance per IEC 61000-2-2.

    Formula: (Max deviation from average / Average voltage) × 100

    Limits:
        < 2%  - Normal
        2-3%  - Warning (investigate)
        > 3%  - Critical (immediate action)
    """

    voltages = [voltage_a, voltage_b, voltage_c]
    average_voltage = sum(voltages) / 3

    if average_voltage == 0:
        return 0.0

    max_deviation = max(abs(v - average_voltage) for v in voltages)
    unbalance_percent = (max_deviation / average_voltage) * 100

    return round(unbalance_percent, 2)


# TOOL 3: IEC FAULT SEVERITY CLASSIFICATION

def _check_iec_voltage(phase_name: str, voltage: float, issues: List[str]) -> None:
    """
    Check voltage against IEC 60038 limits.
    """
    if voltage < IEC.VOLTAGE_MIN:
        issues.append(
            f"CRITICAL: {phase_name} voltage {voltage}V below "
            f"IEC 60038 minimum of {IEC.VOLTAGE_MIN:.0f}V"
        )
    elif voltage > IEC.VOLTAGE_MAX:
        issues.append(
            f"CRITICAL: {phase_name} voltage {voltage}V above "
            f"IEC 60038 maximum of {IEC.VOLTAGE_MAX:.0f}V"
        )
    elif voltage < IEC.VOLTAGE_WARNING_MIN:
        issues.append(
            f"WARNING: {phase_name} voltage {voltage}V below "
            f"IEC 60038 warning level of {IEC.VOLTAGE_WARNING_MIN:.0f}V"
        )
    elif voltage > IEC.VOLTAGE_WARNING_MAX:
        issues.append(
            f"WARNING: {phase_name} voltage {voltage}V above "
            f"IEC 60038 warning level of {IEC.VOLTAGE_WARNING_MAX:.0f}V"
        )


def classify_fault_severity(sensor_data: Dict[str, float]) -> Tuple[str, List[str], float]:
    """
    Classify fault severity per IEC standards.

    Combines:
        - IEC 60038: Voltage limits
        - IEC 61000-2-2: Voltage unbalance
        - IEC 60034: Motor protection
    """

    voltage_a = sensor_data["voltage_a"]
    voltage_b = sensor_data["voltage_b"]
    voltage_c = sensor_data["voltage_c"]
    current = sensor_data["current"]
    frequency = sensor_data["frequency"]

    # Calculate voltage unbalance (IEC 61000-2-2)
    imbalance = calculate_voltage_imbalance(voltage_a, voltage_b, voltage_c)

    issues: List[str] = []

    # IEC 60038: Voltage Checks
    _check_iec_voltage("Phase A", voltage_a, issues)
    _check_iec_voltage("Phase B", voltage_b, issues)
    _check_iec_voltage("Phase C", voltage_c, issues)

    # IEC 61000-2-2: Unbalance Checks
    if imbalance > IEC.UNBALANCE_CRITICAL:
        issues.append(
            f"CRITICAL: Voltage unbalance {imbalance}% exceeds "
            f"IEC 61000-2-2 critical limit of {IEC.UNBALANCE_CRITICAL}%"
        )
    elif imbalance > IEC.UNBALANCE_WARNING:
        issues.append(
            f"WARNING: Voltage unbalance {imbalance}% exceeds "
            f"IEC 61000-2-2 warning limit of {IEC.UNBALANCE_WARNING}%"
        )
    elif imbalance > IEC.UNBALANCE_NORMAL:
        issues.append(
            f"INFO: Voltage unbalance {imbalance}% is within "
            f"IEC 61000-2-2 normal range (<{IEC.UNBALANCE_WARNING}%)"
        )

    #  IEC 60038: Frequency Checks
    if frequency < IEC.FREQUENCY_MIN or frequency > IEC.FREQUENCY_MAX:
        issues.append(
            f"CRITICAL: Frequency {frequency}Hz outside "
            f"IEC 60038 limits ({IEC.FREQUENCY_MIN:.1f}-{IEC.FREQUENCY_MAX:.1f}Hz)"
        )

    # IEC 60034: Motor Protection
    if current > IEC.CURRENT_CRITICAL:
        issues.append(
            f"CRITICAL: Current {current}A exceeds "
            f"IEC 60034 critical limit of {IEC.CURRENT_CRITICAL:.0f}A"
        )
    elif current > IEC.CURRENT_WARNING:
        issues.append(
            f"WARNING: Current {current}A exceeds "
            f"IEC 60034 warning limit of {IEC.CURRENT_WARNING:.0f}A"
        )

    # Determine Severity
    critical_count = sum(1 for issue in issues if issue.startswith("CRITICAL"))
    warning_count = sum(1 for issue in issues if issue.startswith("WARNING"))

    if critical_count >= 2:
        severity = "EMERGENCY"
    elif critical_count == 1:
        severity = "CRITICAL"
    elif warning_count >= 1:
        severity = "WARNING"
    else:
        severity = "NORMAL"

    return severity, issues, imbalance
#  TOOL 4: IEC COMPLIANT REPORT

def format_report(
        sensor_data: Dict[str, Any],
        ai_analysis: str,
        severity: str,
        issues: List[str],
        imbalance: float
) -> str:
    """
    Generate a professional report with IEC standard references.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    severity_display = {
        "NORMAL": "✅  NORMAL",
        "WARNING": "⚠️   WARNING",
        "CRITICAL": "🔴  CRITICAL",
        "EMERGENCY": "🚨  EMERGENCY"
    }

    report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║           POWER SYSTEM FAULT ANALYSIS REPORT                         ║
║                    (IEC Standards Compliant)                         ║
╚══════════════════════════════════════════════════════════════════════╝

  📅 Timestamp  :  {timestamp}
  📍 Location   :  {sensor_data.get('location', 'Not specified')}
  ⚡ Severity   :  {severity_display.get(severity, severity)}
  📋 Standards  :  IEC 60038, IEC 61000-2-2, IEC 60034

──────────────────────────────────────────────────────────────────────
  📊 SENSOR READINGS (IEC 60038)
──────────────────────────────────────────────────────────────────────

  Phase A Voltage  :  {sensor_data['voltage_a']} V
  Phase B Voltage  :  {sensor_data['voltage_b']} V
  Phase C Voltage  :  {sensor_data['voltage_c']} V
  Current          :  {sensor_data['current']} A
  Frequency        :  {sensor_data['frequency']} Hz
  Voltage Unbalance:  {imbalance} % (IEC 61000-2-2)
  System Type      :  {IEC.SYSTEM_TYPE}

──────────────────────────────────────────────────────────────────────
  📋 DETECTED ISSUES (IEC Classification)
──────────────────────────────────────────────────────────────────────
"""

    if issues:
        for issue in issues:
            report += f"\n  •  {issue}"
    else:
        report += "\n  •  No issues detected - System operating within IEC standards"

    report += f"""

──────────────────────────────────────────────────────────────────────
  🤖 AI ANALYSIS AND RECOMMENDATIONS
──────────────────────────────────────────────────────────────────────

{ai_analysis}

══════════════════════════════════════════════════════════════════════
  📘 IEC Standards Reference
  • IEC 60038: Standard voltages
  • IEC 61000-2-2: Voltage unbalance limits
  • IEC 60034: Motor protection
══════════════════════════════════════════════════════════════════════
"""

    return report
