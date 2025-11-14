import locale
import numpy as np
import pandas as pd

from utils.config.logging import init_logger

# Initialize logger
logger = init_logger(name=__name__, level="DEBUG", log_file="logs/app.log")

def format_currency(value, symbol: str = "$", locale_str: str = "en_US") -> str:
    """
    Format numbers as USD/EUR-style currency, localized and compact (K, M, B, T).

    Args:
        value: The numeric value to format (int, float, or str).
        symbol: Currency symbol (default '$', supports '€' and others).
        locale_str: Locale code (e.g. 'en_US', 'fr_FR') for number formatting.

    Returns:
        str: Formatted currency string.
    """
    # Set locale for number formatting (try safely)
    try:
        locale.setlocale(locale.LC_ALL, locale_str)
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')  # fallback to system default

    if value is None or value == "":
        return f"0{symbol}" if symbol == "€" else f"{symbol}0"

    # Convert input to float safely
    try:
        number = float(value)
    except (ValueError, TypeError):
        return f"0{symbol}" if symbol == "€" else f"{symbol}0"

    abs_value = abs(number)

    # Determine compact suffix and scaled value
    if abs_value >= 1_000_000_000_000:
        formatted_value = number / 1_000_000_000_000
        suffix = "T"
    elif abs_value >= 1_000_000_000:
        formatted_value = number / 1_000_000_000
        suffix = "B"
    elif abs_value >= 1_000_000:
        formatted_value = number / 1_000_000
        suffix = "M"
    elif abs_value >= 1_000:
        formatted_value = number / 1_000
        suffix = "K"
    else:
        formatted_value = number
        suffix = ""

    # Localized number formatting (1 decimal place if shortened)
    if suffix:
        formatted_num = locale.format_string("%.1f", formatted_value, grouping=True)
    else:
        formatted_num = locale.format_string("%.0f", formatted_value, grouping=True)

    # Combine with suffix and currency symbol
    formatted = f"{formatted_num}{suffix}"

    # Euro after number, others before
    return f"{formatted}{symbol}" if symbol == "€" else f"{symbol}{formatted}"

def safe_typecast(x, target_type: str = "float"):
    """
    Safely cast a value to int or float.

    Args:
        x: The value to cast (supports Python, NumPy, or pandas numeric types).
        target_type: "int" or "float".

    Returns:
        The casted value, or None if conversion fails.
    """
    # Validate target type early
    if target_type not in {"int", "float"}:
        raise ValueError(f"Invalid target_type '{target_type}', must be 'int' or 'float'")

    # Handle None, NaN, and pandas missing values
    if pd.isna(x):
        return None

    # Strip strings before processing
    if isinstance(x, str):
        x = x.strip()

    # Handle numeric types directly
    if isinstance(x, (int, float, np.integer, np.floating)):
        return int(x) if target_type == "int" else float(x)

    # Attempt safe conversion
    try:
        if target_type == "int":
            return int(float(x))
        else:  # target_type == "float"
            return float(x)
    except (ValueError, TypeError) as e:
        logger.debug(
            "safe_typecast failed",
            extra={"value": x, "target_type": target_type, "error": str(e)}
        )
        return None
