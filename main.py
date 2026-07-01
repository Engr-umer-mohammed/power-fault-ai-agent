
from agent import PowerFaultAgent
import os


def display_welcome():
    """Show welcome screen when agent starts"""

    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           POWER FAULT AI AGENT  v1.0                     ║
║                                                          ║
║      Intelligent Power System Fault Diagnosis            ║
║      Built with Python and Google Gemini AI              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)


def display_menu():
    """Show the main menu options"""

    print("""
─────────────────
  MAIN MENU
──────────────────────────────────────────────────────────
  1.  Analyze new fault
  2.  Run demo fault scenarios
  3.  View fault history summary
  4.  Exit
──────────────────────────────────────────────────────────
    """)


def get_sensor_readings():
    """
    Get real sensor readings from the engineer.
    Handles input errors gracefully.
    """

    print("""
──────────────────────────────────────────────────────────
  ENTER SENSOR READINGS
──────────────────────────────────────────────────────────
    """)

    try:
        location = input("  Location (e.g. Substation A Feeder 1): ").strip()
        if not location:
            location = "Location not specified"

        voltage_a = float(input("  Voltage Phase A (V): "))
        voltage_b = float(input("  Voltage Phase B (V): "))
        voltage_c = float(input("  Voltage Phase C (V): "))
        current   = float(input("  Current (A): "))
        frequency = float(input("  Frequency (Hz): "))

        return {
            "location": location,
            "voltage_a": voltage_a,
            "voltage_b": voltage_b,
            "voltage_c": voltage_c,
            "current": current,
            "frequency": frequency
        }

    except ValueError:
        print("\n  Error: Please enter valid numbers only.")
        print("  Example: 220 not 220V")
        return None


def save_report_to_file(report, fault_number):
    """
    Save the generated report to a text file
    so the engineer can keep a record.
    """

    # Create reports folder if it does not exist
    os.makedirs("reports", exist_ok=True)

    filename = f"reports/fault_report_{fault_number}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"\n  Report saved to: {filename}")


def run_demo_scenarios(agent):
    """
    Run three pre-built demo fault scenarios.
    Shows the agent working on different fault types.
    """

    scenarios = [
        {
            "name": "SCENARIO 1 — Normal System Operation",
            "data": {
                "location": "Substation A Feeder 1",
                "voltage_a": 220,
                "voltage_b": 219,
                "voltage_c": 221,
                "current": 45,
                "frequency": 50.0
            }
        },
        {
            "name": "SCENARIO 2 — Phase B Undervoltage Fault",
            "data": {
                "location": "Substation B Feeder 3",
                "voltage_a": 220,
                "voltage_b": 182,
                "voltage_c": 219,
                "current": 67,
                "frequency": 49.8
            }
        },
        {
            "name": "SCENARIO 3 — Frequency Collapse Emergency",
            "data": {
                "location": "Main Distribution Panel",
                "voltage_a": 210,
                "voltage_b": 208,
                "voltage_c": 211,
                "current": 145,
                "frequency": 47.2
            }
        }
    ]

    print("\n  Running 3 demo fault scenarios...")
    print("  Press Enter after each to continue.\n")

    for i, scenario in enumerate(scenarios, 1):

        print(f"\n{'#' * 58}")
        print(f"  {scenario['name']}")
        print(f"{'#' * 58}")

        report = agent.run(scenario["data"])
        print(report)

        # Save each demo report
        save_report_to_file(report, f"demo_{i}")

        if i < len(scenarios):
            input("  Press Enter for next scenario...")


def view_fault_history(agent):
    """
    Show a summary of all faults
    stored in the agent memory.
    """

    total = agent.memory.get_total_faults()

    print(f"""
──────────────────────────────────────────────────────────
  FAULT HISTORY SUMMARY
──────────────────────────────────────────────────────────
  Total faults analyzed and stored: {total}
──────────────────────────────────────────────────────────
    """)

    if total == 0:
        print("  No faults in memory yet.")
        print("  Run an analysis first.")
        return

    print("  Most recent faults:\n")
    recent = agent.memory.get_recent_faults(count=5)
    print(recent)


def analyze_new_fault(agent):
    """
    Complete workflow for analyzing a new fault.
    Gets readings from engineer and runs agent.
    """

    sensor_data = get_sensor_readings()

    if sensor_data is None:
        print("\n  Analysis cancelled due to invalid input.")
        return

    # Run the complete agent
    report = agent.run(sensor_data)
    print(report)

    # Ask if engineer wants to save the report
    save = input("  Save this report to file? (y/n): ").strip().lower()
    if save == "y":
        fault_number = agent.memory.get_total_faults()
        save_report_to_file(report, fault_number)


def main():
    """
    Main program loop.
    Runs until engineer chooses to exit.
    """

    display_welcome()

    # Initialize the agent once
    print("  Initializing AI Agent...")
    agent = PowerFaultAgent()

    # Main program loop
    while True:

        display_menu()

        choice = input("  Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            analyze_new_fault(agent)

        elif choice == "2":
            run_demo_scenarios(agent)

        elif choice == "3":
            view_fault_history(agent)

        elif choice == "4":
            print("""
──────────────────────────────────────────────────────────
  Thank you for using Power Fault AI Agent.
  All fault records have been saved.
  Goodbye.
──────────────────────────────────────────────────────────
            """)
            break

        else:
            print("\n  Invalid choice. Please enter 1, 2, 3, or 4.")


# Entry point
if __name__ == "__main__":
    main()

