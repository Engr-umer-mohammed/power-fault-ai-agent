
import pandas as pd
import json
import os
import re
from datetime import datetime

class SensorFileHandler:
    """
    Reads sensor data from uploaded files.

    Supports:
        CSV   — from SCADA and data loggers
        Excel — from energy meters and reports
        JSON  — from IoT sensors and APIs
        TXT   — from simple data exports (FAST PATH)
    """

    def __init__(self):
        # Column name variations engineers use
        # Different SCADA systems use different names
        self.voltage_a_names = [
            "voltage_a", "va", "v_a", "phase_a",
            "voltage_phase_a", "van", "v1", "ua",
            "phase a", "volt_a", "voltagea"
        ]
        self.voltage_b_names = [
            "voltage_b", "vb", "v_b", "phase_b",
            "voltage_phase_b", "vbn", "v2", "ub",
            "phase b", "volt_b", "voltageb"
        ]
        self.voltage_c_names = [
            "voltage_c", "vc", "v_c", "phase_c",
            "voltage_phase_c", "vcn", "v3", "uc",
            "phase c", "volt_c", "voltagec"
        ]
        self.current_names = [
            "current", "i", "current_a", "amps",
            "ampere", "load_current", "ia", "il",
            "line_current", "current_total"
        ]
        self.frequency_names = [
            "frequency", "freq", "hz", "f",
            "system_frequency", "grid_frequency",
            "frequency_hz"
        ]
        self.location_names = [
            "location", "site", "substation",
            "feeder", "station", "name", "place",
            "description", "source"
        ]

    def read_file(self, file_path):
        """
        Main method — reads any supported file format.
        Automatically detects format from extension.

        FAST PATH: TXT files bypass pandas/Excel libraries

        Returns:
            list of sensor_data dictionaries
            one dictionary per reading/row
        """

        extension = os.path.splitext(
            file_path
        )[1].lower()

        print(f"Reading file: {file_path}")
        print(f"Format detected: {extension}")

        # ─── OPTIMIZATION: TXT files get FAST PATH ───
        if extension == ".txt":
            return self._read_txt_fast(file_path)

        elif extension == ".csv":
            return self._read_csv(file_path)

        elif extension in [".xlsx", ".xls"]:
            return self._read_excel(file_path)

        elif extension == ".json":
            return self._read_json(file_path)

        else:
            return None, (
                f"Unsupported file format: {extension}\n"
                f"Supported formats: CSV, Excel, JSON, TXT"
            )

    # FAST TXT PARSER

    def _read_txt_fast(self, file_path):
        """
        FAST TXT parser - minimal overhead.
        Designed for maximum speed with TXT files.
        """
        readings = []

        try:
            with open(file_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # ─── Fast path: Try key:value format ───
                # This catches "voltage_a: 220" style
                key_value_pattern = r'(\w+)\s*[:=]\s*([\d.]+)'
                matches = re.findall(key_value_pattern, line)

                if matches:
                    sensor_data = {}
                    for key, value in matches:
                        key = key.lower()
                        if key in ['voltage_a', 'va', 'v_a']:
                            sensor_data['voltage_a'] = float(value)
                        elif key in ['voltage_b', 'vb', 'v_b']:
                            sensor_data['voltage_b'] = float(value)
                        elif key in ['voltage_c', 'vc', 'v_c']:
                            sensor_data['voltage_c'] = float(value)
                        elif key in ['current', 'i']:
                            sensor_data['current'] = float(value)
                        elif key in ['frequency', 'freq', 'hz', 'f']:
                            sensor_data['frequency'] = float(value)

                    if all(k in sensor_data for k in ['voltage_a', 'voltage_b', 'voltage_c', 'current', 'frequency']):
                        sensor_data['location'] = "TXT File Import"
                        readings.append(sensor_data)
                    continue

                # ─── Second path: Try comma/space separated ───
                # This catches "220, 218, 221, 45, 50.0" style
                numbers = re.findall(r'[\d.]+', line)
                if len(numbers) >= 5:
                    try:
                        reading = {
                            "voltage_a": float(numbers[0]),
                            "voltage_b": float(numbers[1]),
                            "voltage_c": float(numbers[2]),
                            "current": float(numbers[3]),
                            "frequency": float(numbers[4]),
                            "location": "TXT File Import"
                        }
                        readings.append(reading)
                    except:
                        pass

            if readings:
                return readings, None
            else:
                return None, "No valid sensor readings found in TXT file"

        except Exception as e:
            return None, f"Error reading TXT file: {e}"

    # CSV PARSER
    def _read_csv(self, file_path):
        """
        Read sensor data from CSV file.
        Handles different CSV formats automatically.
        """
        try:
            # Try reading with different separators
            for separator in [",", ";", "\t"]:
                try:
                    df = pd.read_csv(
                        file_path,
                        sep=separator
                    )
                    if len(df.columns) >= 3:
                        break
                except:
                    continue

            return self._parse_dataframe(df, "CSV")

        except Exception as e:
            return None, f"Error reading CSV file: {e}"

    # EXCEL PARSER
    def _read_excel(self, file_path):
        """
        Read sensor data from Excel file.
        Reads the first sheet automatically.
        """
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=0
            )
            return self._parse_dataframe(df, "Excel")

        except Exception as e:
            return None, f"Error reading Excel file: {e}"

    #  JSON PARSER

    def _read_json(self, file_path):
        """
        Read sensor data from JSON file.
        Handles both single reading and arrays.
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Handle array of readings
            if isinstance(data, list):
                readings = []
                for item in data:
                    reading = self._extract_from_dict(item)
                    if reading:
                        readings.append(reading)
                return readings, None

            # Handle single reading
            elif isinstance(data, dict):
                reading = self._extract_from_dict(data)
                if reading:
                    return [reading], None
                else:
                    return None, (
                        "Could not find sensor data in JSON file"
                    )

        except Exception as e:
            return None, f"Error reading JSON file: {e}"

    # DATAFRAME PARSER

    def _parse_dataframe(self, df, file_type):
        """
        Parse a pandas DataFrame into
        standardized sensor data dictionaries.
        Works for both CSV and Excel.
        """

        # Normalize column names to lowercase
        df.columns = [
            str(col).lower().strip()
            for col in df.columns
        ]

        print(f"Columns found: {list(df.columns)}")

        # Find which columns match our sensor names
        col_voltage_a = self._find_column(
            df, self.voltage_a_names
        )
        col_voltage_b = self._find_column(
            df, self.voltage_b_names
        )
        col_voltage_c = self._find_column(
            df, self.voltage_c_names
        )
        col_current = self._find_column(
            df, self.current_names
        )
        col_frequency = self._find_column(
            df, self.frequency_names
        )
        col_location = self._find_column(
            df, self.location_names
        )

        # Check required columns exist
        missing = []
        if not col_voltage_a:
            missing.append("Voltage Phase A")
        if not col_voltage_b:
            missing.append("Voltage Phase B")
        if not col_voltage_c:
            missing.append("Voltage Phase C")
        if not col_current:
            missing.append("Current")
        if not col_frequency:
            missing.append("Frequency")

        if missing:
            return None, (
                f"Could not find these columns in "
                f"your {file_type} file:\n"
                + "\n".join(f"  • {m}" for m in missing)
                + f"\n\nColumns found in file:\n"
                + "\n".join(
                    f"  • {c}" for c in df.columns
                )
            )

        # Build list of sensor readings
        readings = []

        for index, row in df.iterrows():
            try:
                location = (
                    str(row[col_location])
                    if col_location
                    else f"{file_type} Row {index + 1}"
                )

                reading = {
                    "voltage_a": float(
                        row[col_voltage_a]
                    ),
                    "voltage_b": float(
                        row[col_voltage_b]
                    ),
                    "voltage_c": float(
                        row[col_voltage_c]
                    ),
                    "current": float(
                        row[col_current]
                    ),
                    "frequency": float(
                        row[col_frequency]
                    ),
                    "location": location
                }
                readings.append(reading)

            except Exception as e:
                print(f"Skipping row {index}: {e}")
                continue

        if readings:
            return readings, None
        else:
            return None, (
                f"No valid readings found in {file_type} file"
            )

    # HELPER METHODS

    def _find_column(self, df, possible_names):
        """
        Find the correct column name in the dataframe
        by checking all possible name variations.
        """
        for name in possible_names:
            if name in df.columns:
                return name
        return None

    def _extract_from_dict(self, data):
        """
        Extract sensor readings from a dictionary.
        Used for JSON file parsing.
        """
        reading = {}

        # Try each possible name for each field
        for names, key in [
            (self.voltage_a_names, "voltage_a"),
            (self.voltage_b_names, "voltage_b"),
            (self.voltage_c_names, "voltage_c"),
            (self.current_names,   "current"),
            (self.frequency_names, "frequency"),
        ]:
            for name in names:
                if name in data:
                    try:
                        reading[key] = float(data[name])
                        break
                    except:
                        pass

        # Get location if available
        for name in self.location_names:
            if name in data:
                reading["location"] = str(data[name])
                break

        # Check all required fields found
        required = [
            "voltage_a", "voltage_b", "voltage_c",
            "current", "frequency"
        ]
        if all(k in reading for k in required):
            if "location" not in reading:
                reading["location"] = "JSON Import"
            return reading

        return None

    def generate_file_summary(self, readings):
        """
        Generate a summary of what was found
        in the uploaded file.
        """
        if not readings:
            return "No readings found"

        summary = (
            f"📊 File Analysis Summary\n"
            f"{'=' * 35}\n"
            f"Total readings found: {len(readings)}\n\n"
        )

        # Show first 5 readings max (to avoid huge messages)
        max_display = min(5, len(readings))
        for i, r in enumerate(readings[:max_display], 1):
            summary += (
                f"Reading {i}:\n"
                f"  Location : {r.get('location', 'N/A')}\n"
                f"  Voltage A: {r.get('voltage_a')} V\n"
                f"  Voltage B: {r.get('voltage_b')} V\n"
                f"  Voltage C: {r.get('voltage_c')} V\n"
                f"  Current  : {r.get('current')} A\n"
                f"  Frequency: {r.get('frequency')} Hz\n\n"
            )

        if len(readings) > 5:
            summary += f"... and {len(readings) - 5} more readings\n"

        return summary