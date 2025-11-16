#!/usr/bin/env python3
import argparse, logging, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Clean, readable logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('orch')


def run_step(fn, *args, retries=2, name=None):
    """
    Run a single pipeline step with retries and clean logging.

    fn     : function to run
    args   : arguments to the function
    retries: how many times to retry if it fails
    name   : user-friendly name for logging
    """

    name = name or getattr(fn, '__name__', str(fn))

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"▶ Running step: {name} (attempt {attempt}/{retries})")
            result = fn(*args)
            logger.info(f"✔ Completed step: {name}")
            return result

        except Exception as e:
            logger.exception(f"❌ Step failed: {name} — {e}")
            if attempt < retries:
                logger.info("⏳ Retrying in 2 seconds…")
                time.sleep(2)
            else:
                raise


# -----------------------------
#  OCEAN PIPELINE
# -----------------------------

def ocean_pipeline():
    """
    Full pipeline for ocean data:
    1. Ingest → NetCDF
    2. Clean → JSONL
    3. Produce → Kafka
    """

    logger.info("\n🌊 ===== Starting OCEAN Pipeline =====")

    from pipeline.ocean import ingest as i, clean as c, produce as p

    nc_path = run_step(i.ingest, name='ocean.ingest')
    logger.info(f"   → Ingested raw NetCDF file: {nc_path}")

    cleaned_path = run_step(c.clean, nc_path, name='ocean.clean')
    logger.info(f"   → Cleaned JSONL file created: {cleaned_path}")

    run_step(p.produce, cleaned_path, name='ocean.produce')
    logger.info("   → All cleaned data successfully pushed to Kafka")

    logger.info("🌊 ===== OCEAN Pipeline Completed =====\n")


# ----------------------------------------------------------
# COMMENTING OUT REMAINING DOMAINS UNTIL THEY ARE READY
# ----------------------------------------------------------

"""
def fisheries_pipeline():
    logger.info("\n🐟 ===== Starting FISHERIES Pipeline =====")
    from pipeline.fisheries import ingest as i, clean as c, produce as p

    files = run_step(i.ingest, name='fisheries.ingest')
    cleaned = run_step(c.clean, files, name='fisheries.clean')
    run_step(p.produce, cleaned, name='fisheries.produce')

    logger.info("🐟 ===== Fisheries Pipeline Completed =====\n")


def biodiversity_pipeline():
    logger.info("\n🧬 ===== Starting BIODIVERSITY Pipeline =====")
    from pipeline.biodiversity import ingest as i, clean as c, produce as p

    files = run_step(i.ingest, name='biodiv.ingest')
    cleaned = run_step(c.clean, files, name='biodiv.clean')
    run_step(p.produce, cleaned, name='biodiv.produce')

    logger.info("🧬 ===== Biodiversity Pipeline Completed =====\n")
"""


# Only the ocean pipeline is currently active
DOMAIN_MAP = {
    'ocean': ocean_pipeline,
    # 'fisheries': fisheries_pipeline,
    # 'biodiversity': biodiversity_pipeline
}


def run_domains(domains, parallel=False):
    """
    Run one or more selected domains, optionally in parallel.
    For now, only 'ocean' is enabled.
    """

    if parallel:
        logger.info("Running pipelines in PARALLEL mode")
        with ThreadPoolExecutor(max_workers=len(domains)) as ex:
            futures = {ex.submit(DOMAIN_MAP[d]): d for d in domains}
            for fut in as_completed(futures):
                d = futures[fut]
                try:
                    fut.result()
                    logger.info(f"✔ Domain finished: {d}")
                except Exception as e:
                    logger.exception(f"❌ Domain {d} failed: {e}")
    else:
        for d in domains:
            logger.info(f"▶ Starting domain: {d}")
            DOMAIN_MAP[d]()
            logger.info(f"✔ Domain completed: {d}")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--domain', '-d', default='ocean')   # default changed
    p.add_argument('--parallel', '-p', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    dom = args.domain.lower()

    # Only run ocean for now
    if dom not in DOMAIN_MAP:
        print("Currently only 'ocean' is available.")
        sys.exit(1)

    run_domains([dom], parallel=args.parallel)


if __name__ == '__main__':
    main()
