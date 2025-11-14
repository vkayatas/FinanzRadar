def safe_strftime(value, fmt="%Y-%m-%d"):
    if value is None:
        return None
    # Unpack if it's a list
    if isinstance(value, list):
        value = value[0] if value else None
    return value.strftime(fmt) if value else None