from pathlib import Path
BASE = Path('/data')
def RAW_PATH(domain): return BASE / 'raw' / domain
def CLEAN_PATH(domain): return BASE / 'clean' / domain
def OUTPUT_PATH(domain): return BASE / 'output' / domain
