from datetime import datetime
def validate_ocean_row(r: dict) -> dict:
    try:
        return {
            "time": str(r["time"]),
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "depth": float(r.get("depth", 0)) if r.get("depth") is not None else None,
            "so": float(r["so"]),
            "thetao": float(r["thetao"]),
            "uo": float(r["uo"]),
            "vo": float(r["vo"]),
        }
    except Exception as e:
        raise ValueError(f"Schema validation failed for ocean row: {e}")

def validate_dwc(rec: dict):
    # generic DWC minimal validation
    if not rec.get('eventDate'):
        raise ValueError('Missing eventDate')
    if rec.get('measurementValue') is None and rec.get('decimalLatitude') is None:
        raise ValueError('Must have measurementValue or coordinates')
    return rec
