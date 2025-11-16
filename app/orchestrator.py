#!/usr/bin/env python3
import argparse, logging, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Crisp logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('orch')


def narrate(msg):
    print(f"\n👉 {msg}\n")


def run_step(fn, *args, retries=2, name=None):
    """
    Wrapper to run pipeline steps with retries and interactive narration.
    """
    name = name or getattr(fn, '__name__', str(fn))
    narrate(f"Starting step: {name}")

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"▶ Running {name} (attempt {attempt}/{retries})")
            result = fn(*args)
            logger.info(f"✔ Completed {name}")
            narrate(f"Finished step: {name}")
            return result

        except Exception as e:
            logger.error(f"❌ Error in {name}: {e}")

            if attempt < retries:
                logger.info("⏳ Retrying in 2 seconds…")
                time.sleep(2)
            else:
                narrate(f"Step failed permanently: {name}")
                raise


# -----------------------------
# PIPELINES
# -----------------------------

def ocean_pipeline():
    narrate("🌊 Starting OCEAN Pipeline")
    from pipeline.ocean import ingest as i, clean as c, produce as p

    nc_path = run_step(i.ingest, name='ocean.ingest')
    cleaned = run_step(c.clean, nc_path, name='ocean.clean')
    run_step(p.produce, cleaned, name='ocean.produce')

    narrate("🌊 OCEAN Pipeline Completed")


def fisheries_pipeline():
    narrate("🐟 Starting FISHERIES Pipeline")
    from pipeline.fisheries import ingest as i, clean as c, produce as p

    files = run_step(i.ingest, name='fisheries.ingest')
    cleaned = run_step(c.clean, files, name='fisheries.clean')
    run_step(p.produce, cleaned, name='fisheries.produce')

    narrate("🐟 FISHERIES Pipeline Completed")


def biodiversity_pipeline():
    narrate("🧬 Starting BIODIVERSITY Pipeline")
    
    from pipeline.biodiversity import ingest as i, clean as c, merge as m, produce as p
    
    files = run_step(i.ingest, name='biodiversity.ingest')
    cleaned_dir = run_step(c.clean, files, name='biodiversity.clean')
    merged_jsonl = run_step(m.merge, cleaned_dir, name='biodiversity.merge')
    run_step(p.produce, merged_jsonl, name='biodiversity.produce')

    narrate("🧬 BIODIVERSITY Pipeline Completed")


# -----------------------------
# DOMAIN REGISTRATION
# -----------------------------

DOMAIN_MAP = {
    'ocean': ocean_pipeline,
    'fisheries': fisheries_pipeline,
    'biodiversity': biodiversity_pipeline
}


# -----------------------------
# EXECUTION HANDLER
# -----------------------------

def run_domains(domains, parallel=False):

    narrate("🚀 Orchestrator Starting")

    if parallel and len(domains) > 1:
        narrate("Running all selected domains in PARALLEL mode")

        with ThreadPoolExecutor(max_workers=len(domains)) as ex:
            futures = {ex.submit(DOMAIN_MAP[d]): d for d in domains}

            for fut in as_completed(futures):
                d = futures[fut]
                try:
                    fut.result()
                    narrate(f"✔ Domain completed: {d}")
                except Exception as e:
                    narrate(f"❌ Domain {d} failed: {e}")

    else:
        narrate("Running domains in SERIES mode")
        for d in domains:
            narrate(f"▶ Running domain: {d}")
            DOMAIN_MAP[d]()
            narrate(f"✔ Finished domain: {d}")


# -----------------------------
# ARGUMENTS
# -----------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Unified Marine Data Orchestrator"
    )
    parser.add_argument(
        "--domain", "-d",
        default="ocean",
        help="Comma-separated list: ocean,fisheries,biodiversity"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run all selected domains in parallel"
    )
    return parser.parse_args()


# -----------------------------
# MAIN ENTRY
# -----------------------------

def main():
    narrate("🔧 Initializing Orchestrator")
    args = parse_args()

    domains = [d.strip() for d in args.domain.split(",")]
    for d in domains:
        if d not in DOMAIN_MAP:
            narrate(f"❌ Invalid domain: {d}")
            sys.exit(1)

    narrate(f"Selected domains → {domains}")
    run_domains(domains, parallel=args.parallel)

    narrate("🎉 All pipelines completed successfully!")


if __name__ == "__main__":
    main()
