from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.dataset_builder import TRAINING_DATASET_PATH, build_training_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GreySignal country-year training dataset.")
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--hs-code", default="TOTAL")
    parser.add_argument("--fast", action="store_true", help="Skip slower GDELT and UN Comtrade calls.")
    args = parser.parse_args()

    dataset = build_training_dataset(
        start_year=args.start_year,
        end_year=args.end_year,
        hs_code=args.hs_code,
        include_slow_sources=not args.fast,
    )
    print(f"Wrote {len(dataset)} rows to {TRAINING_DATASET_PATH}")
    print(dataset[["country_name", "year", "final_risk_score", "risk_label"]].tail(10).to_string(index=False))


if __name__ == "__main__":
    main()
