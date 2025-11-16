from datetime import datetime, timedelta
import copernicusmarine
from pipeline.common.paths import RAW_PATH
from dotenv import load_dotenv
import os

load_dotenv()  # reads from .env automatically
username = os.getenv("COPERNICUS_USERNAME")
password = os.getenv("COPERNICUS_PASSWORD")

def ingest():
    raw_dir = RAW_PATH("ocean")
    raw_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    outfile = raw_dir / f"ocean_{timestamp}.nc"

    copernicusmarine.subset(
        username = username,
        password = password,
        dataset_id="cmems_mod_glo_phy_anfc_0.083deg_PT1H-m",
        variables=["so", "thetao", "uo", "vo", "zos"],
        minimum_longitude=62.7624394824933,
        maximum_longitude=95.10309461377467,
        minimum_latitude=3.1228444517411815,
        maximum_latitude=25.964845628380452,
        start_datetime=datetime.now() - timedelta(days = 2),
        end_datetime=datetime.now() - timedelta(days = 1),
        minimum_depth=0.49402499198913574,
        maximum_depth=0.49402499198913574,
        output_filename=str(outfile)
    )
    
    return str(outfile)

if __name__ == "__main__":
    print(ingest())
