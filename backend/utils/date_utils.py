import datetime
import pandas as pd

def _dates_to_quarters(self, dates: pd.Series, quarterly:bool) -> pd.Series:
    dates = pd.to_datetime(dates)

    if not quarterly:
        return dates.dt.year.map(lambda y: f"CY{y}")
        # # Annual reports: map to nearest year-end
        # def nearest_year(dt):
        #     dec31 = pd.Timestamp(year=dt.year, month=12, day=31)
        #     # if date is closer to previous year's Dec 31, subtract 1
        #     return f"CY{dt.year - 1}" if (dt - dec31).days < -183 else f"CY{dt.year}"

        # return dates.apply(nearest_year)
    
    else:
        # Quarterly reports: map to nearest canonical quarter end
        return dates.apply(nearest_quarter)

def nearest_quarter(dt):
    year = dt.year
    quarters = {
        pd.Timestamp(f"{year}-03-31"): f"CY{year}Q1",
        pd.Timestamp(f"{year}-06-30"): f"CY{year}Q2",
        pd.Timestamp(f"{year}-09-30"): f"CY{year}Q3",
        pd.Timestamp(f"{year}-12-31"): f"CY{year}Q4",
    }
    nearest = min(quarters.keys(), key=lambda x: abs(x - dt))
    return quarters[nearest]
     
def safe_strftime(value, fmt="%Y-%m-%d"):
    if value is None:
        return None
    # Unpack if it's a list
    if isinstance(value, list):
        value = value[0] if value else None
    return value.strftime(fmt) if value else None

def safe_dt(val):
    """Safely get a datetime and format as YYYY-MM-DD.
    Handles single datetime or a list with one datetime.
    Returns None if input is None or invalid.
    """
    if val is None:
        return None
    if isinstance(val, list) and val:
        val = val[0]  # unpack first element
    if val is not None:
        return val.strftime("%Y-%m-%d")
    return None

def delta_hours_from_date(date_obj, ts, tz: str = "UTC") -> float:
    """
    Calculate the absolute delta hours between date_obj and ts.

    Args:
        date_obj: datetime.date, datetime.datetime, pandas.Timestamp, string, or None
        ts: datetime.date, datetime.datetime, pandas.Timestamp, string, or None
        tz: timezone string for conversion (default "UTC")

    Returns:
        float: absolute delta hours, or None if either input is None/invalid
    """
    import datetime
    import pandas as pd

    def to_datetime(x):
        if x is None:
            return None
        if isinstance(x, datetime.datetime):
            dt = x
        elif isinstance(x, datetime.date):
            dt = datetime.datetime.combine(x, datetime.time.min)
        else:
            try:
                dt = pd.to_datetime(x)
            except Exception:
                return None
        if dt.tzinfo is None:
            dt = pd.Timestamp(dt).tz_localize("UTC")
        return dt.tz_convert(tz).to_pydatetime()

    date_dt = to_datetime(date_obj)
    ts_dt = to_datetime(ts)

    if date_dt is None or ts_dt is None:
        return None

    # Absolute delta between the two datetimes
    delta_hours = abs((date_dt - ts_dt).total_seconds() / 3600)
    return round(delta_hours, 2)
