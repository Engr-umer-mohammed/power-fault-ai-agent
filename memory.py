
import json
import os
from datetime import datetime
class AgentMemory:
    """
    Manages everything the agent remembers.

    Think of this like a logbook that
    a power engineer keeps at a substation.
    Every fault event is recorded with:
       - When it happened
       - What the readings were
       - What the AI concluded
    """

    def __init__(
        self,
        memory_file="fault_history.json",
        reports_folder="reports"
    ):
        """
        Initialize the memory system.
        memory_file is where all faults are saved on disk.
        reports_folder is where human-readable TXT reports are saved.

        Uses absolute paths so files always save
        in the project folder regardless of
        which file runs the agent —
        main.py or telegram_bot.py or any future file.
        """

        # Find the absolute location of this file
        # This is always the project folder
        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        # Build absolute paths for both storage locations
        self.memory_file = os.path.join(
            base_dir, memory_file
        )
        self.reports_folder = os.path.join(
            base_dir, reports_folder
        )

        self.fault_history = []

        # Create reports folder if it does not exist
        try:
            if not os.path.exists(self.reports_folder):
                os.makedirs(self.reports_folder)
                print(
                    f"📁 Created reports folder: "
                    f"{self.reports_folder}"
                )
        except Exception as e:
            print(
                f"⚠️ Could not create reports folder: {e}"
            )

        # Load any existing memory when agent starts
        self.load_memory()

    def load_memory(self):
        """
        Load past fault records from the saved file.
        If no file exists yet — start with empty memory.
        This runs automatically when agent starts.
        """

        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as file:
                    self.fault_history = json.load(file)
                print(
                    f"Memory loaded successfully. "
                    f"Past faults found: "
                    f"{len(self.fault_history)}"
                )
            except Exception as e:
                print(f"⚠️ Error loading memory: {e}")
                self.fault_history = []
        else:
            print("No past memory found. Starting fresh.")
            self.fault_history = []

    def save_fault(self, sensor_data, analysis_result):
        """
        Save a new fault event to memory.
        Called every time agent analyzes a fault.
        Saves in two formats automatically:
           1. JSON  — fault_history.json
           2. Text  — reports/timestamp_location.txt

        sensor_data     — the voltage and current readings
        analysis_result — what the AI concluded
        """

        # Build the complete fault record
        fault_record = {
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "sensor_data": sensor_data,
            "analysis": analysis_result
        }

        # Add to our in-memory list
        self.fault_history.append(fault_record)

        # SAVE 1 — JSON memory file
        try:
            with open(self.memory_file, "w") as file:
                json.dump(
                    self.fault_history,
                    file,
                    indent=4
                )
            print(f"💾 JSON saved: {self.memory_file}")
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")

        # SAVE 2 — Human readable text file
        self._save_human_readable(fault_record)

        print(
            f"Fault saved to memory. "
            f"Total records stored: "
            f"{len(self.fault_history)}"
        )

    def _save_human_readable(self, fault_record):
        """
        Save a human-readable TXT version
        of the fault report.

        Creates one text file per fault.
        Named by timestamp and location.
        Saved in the reports folder.
        Works correctly whether called
        from main.py or telegram_bot.py.
        """

        try:
            # Build filename from timestamp
            timestamp = fault_record[
                "timestamp"
            ].replace(":", "-").replace(" ", "_")

            # Get location and clean it for filename
            location = fault_record[
                "sensor_data"
            ].get("location", "unknown_location")

            clean_location = (
                location
                .replace(" ", "_")
                .replace("/", "-")
                .replace(":", "-")
            )

            # Build the complete file path
            filename = os.path.join(
                self.reports_folder,
                f"fault_report_{timestamp}"
                f"_{clean_location}.txt"
            )

            # Create reports folder if missing
            if not os.path.exists(self.reports_folder):
                os.makedirs(self.reports_folder)

            # Write the complete report
            with open(
                filename, "w", encoding="utf-8"
            ) as f:

                # Header
                f.write("=" * 70 + "\n")
                f.write(
                    "        POWER SYSTEM FAULT "
                    "ANALYSIS REPORT\n"
                )
                f.write("=" * 70 + "\n\n")

                # Timestamp and location
                f.write(
                    f"  Timestamp : "
                    f"{fault_record['timestamp']}\n"
                )
                f.write(
                    f"  Location  : "
                    f"{fault_record['sensor_data'].get('location', 'Not specified')}\n\n"
                )

                # Sensor readings
                f.write("-" * 70 + "\n")
                f.write("  SENSOR READINGS\n")
                f.write("-" * 70 + "\n\n")

                data = fault_record["sensor_data"]
                f.write(
                    f"  Phase A Voltage  : "
                    f"{data.get('voltage_a', 'N/A')} V\n"
                )
                f.write(
                    f"  Phase B Voltage  : "
                    f"{data.get('voltage_b', 'N/A')} V\n"
                )
                f.write(
                    f"  Phase C Voltage  : "
                    f"{data.get('voltage_c', 'N/A')} V\n"
                )
                f.write(
                    f"  Current          : "
                    f"{data.get('current', 'N/A')} A\n"
                )
                f.write(
                    f"  Frequency        : "
                    f"{data.get('frequency', 'N/A')} Hz\n\n"
                )

                # AI analysis
                f.write("-" * 70 + "\n")
                f.write(
                    "  AI ANALYSIS AND RECOMMENDATIONS\n"
                )
                f.write("-" * 70 + "\n\n")
                f.write(fault_record["analysis"])
                f.write("\n\n" + "=" * 70 + "\n")

            print(
                f"  📄 Text report saved: "
                f"{filename}"
            )
            return filename

        except Exception as e:
            print(
                f"  ❌ Error saving text report: {e}"
            )
            import traceback
            traceback.print_exc()
            return None

    def get_recent_faults(self, count=3):
        """
        Get the most recent fault records.
        Used to give the AI agent context
        about what happened recently
        so it can spot patterns.

        count — how many recent faults to return
        """

        if len(self.fault_history) == 0:
            return "No previous fault history available."

        recent = self.fault_history[-count:]
        summary_lines = []

        for fault in recent:
            line = (
                f"Time: {fault['timestamp']} | "
                f"Phase A: "
                f"{fault['sensor_data']['voltage_a']}V | "
                f"Phase B: "
                f"{fault['sensor_data']['voltage_b']}V | "
                f"Phase C: "
                f"{fault['sensor_data']['voltage_c']}V | "
                f"Summary: {fault['analysis'][:80]}..."
            )
            summary_lines.append(line)

        return "\n".join(summary_lines)

    def get_total_faults(self):
        """
        Return total number of faults
        stored in memory.
        """
        return len(self.fault_history)

    def clear_memory(self):
        """
        Clear all stored fault history.
        Use carefully — this cannot be undone.
        """
        self.fault_history = []

        if os.path.exists(self.memory_file):
            os.remove(self.memory_file)

        print("Memory cleared successfully.")