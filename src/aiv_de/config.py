from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    data_dir: str = os.getenv("AIVDE_DATA_DIR", "./data")
    policy_dir: str = os.getenv("AIVDE_POLICY_DIR", "./policy_store")
    sqlite_path: str = os.getenv("AIVDE_SQLITE_PATH", "./aivde_memory.sqlite")
    model_name: str = os.getenv("AIVDE_MODEL_NAME", "gpt-4o-mini")  # safe default
    max_retries: int = int(os.getenv("AIVDE_MAX_RETRIES", "2"))
    # for debugging llm prompt exchanges - AB
    log_llm_io = os.getenv("AIVDE_LOG_LLM_IO", "0") == "1"
    llm_log_dir = os.getenv("AIVDE_LLM_LOG_DIR", "./out/debug_llm")


SETTINGS = Settings()

# for debugging llm prompt exchanges - AB
AIVDE_ANNOTATE_ADR=1