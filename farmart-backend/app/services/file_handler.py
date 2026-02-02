"""
File Handler
CSV parsing for bulk uploads & Image processing
"""

import pandas as pd
import io
from werkzeug.utils import secure_filename


class FileHandler:
    """Handler for file uploads and processing."""

    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}
    MAX_FILE_SIZE = 16 * 1024 * 1024

    @classmethod
    def allowed_file(cls, filename):
        """Check if file extension is allowed."""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in cls.ALLOWED_EXTENSIONS
        )

    @classmethod
    def parse_livestock_file(cls, file):
        """Parse CSV or Excel file for livestock bulk upload."""
        if not cls.allowed_file(file.filename):
            raise ValueError("File type not allowed. Please upload CSV or Excel file.")

        filename = secure_filename(file.filename)
        file_content = file.read()

        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_content))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_content))
        else:
            raise ValueError("Unsupported file format")

        df = cls._clean_dataframe(df)
        data = df.to_dict(orient="records")

        summary = {
            "total_rows": len(data),
            "species_found": df["species"].unique().tolist()
            if "species" in df.columns
            else [],
            "columns": list(df.columns),
        }

        return {"data": data, "summary": summary}

    @classmethod
    def _clean_dataframe(cls, df):
        """Clean and validate dataframe."""
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace("nan", "")

        df = df.fillna("")

        required_mapping = {"name": "Unnamed Animal", "species": "unknown", "price": 0}

        for col, default in required_mapping.items():
            if col not in df.columns:
                df[col] = default

        return df

    @classmethod
    def validate_livestock_data(cls, data):
        """Validate livestock data from bulk upload."""
        valid_data = []
        errors = []

        required_fields = ["species", "price"]
        valid_species = ["cattle", "goat", "sheep", "pig", "chicken", "turkey", "duck"]

        for idx, item in enumerate(data):
            row_errors = []

            for field in required_fields:
                if not item.get(field):
                    row_errors.append(f"Missing required field: {field}")

            try:
                price = float(item.get("price", 0))
                if price <= 0:
                    row_errors.append("Price must be greater than 0")
            except (ValueError, TypeError):
                row_errors.append("Invalid price format")

            if item.get("species") and item["species"].lower() not in valid_species:
                row_errors.append(
                    f"Invalid species. Must be one of: {', '.join(valid_species)}"
                )

            if row_errors:
                errors.append(f"Row {idx + 1}: {', '.join(row_errors)}")
            else:
                valid_data.append(item)

        return valid_data, errors
