"""conduction-lens CLI. `python -m conduction_lens run|report ...`."""

from __future__ import annotations

import argparse

from . import pipeline
from .config import RunConfig


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="conduction-lens",
        description="Amortized + calibrated Purkinje conduction identifiability from the ECG.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run the full pipeline (sweep -> NPE + conformal -> Contract-B)")
    r.add_argument(
        "--geometry", default="crtdemo", help="crtdemo (wired); strocchi/medalcare stubs"
    )
    r.add_argument("--dim", type=int, default=7, help="parameter count (frozen contract = 7)")
    r.add_argument("--budget", type=int, default=5000, help="total usable sims (train + calib)")
    r.add_argument("--obs", default="features", choices=["features", "waveform"])
    r.add_argument("--out", default="runs/crtdemo_7d", help="run directory for artifacts")
    r.add_argument("--seed", type=int, default=1234)
    r.add_argument("--ppc-n", type=int, default=8, help="posterior-predictive band forwards")
    r.add_argument("--workers", type=int, default=0, help="0 = auto (min(cpu, 8))")
    r.add_argument("--dry-run", action="store_true", help="tiny budget to validate the path")

    rep = sub.add_parser("report", help="print the headline summary of a finished run dir")
    rep.add_argument("out", help="run directory containing results.json")

    args = p.parse_args(argv)
    if args.cmd == "run":
        pipeline.run(
            RunConfig(
                geometry=args.geometry,
                dim=args.dim,
                budget=args.budget,
                obs=args.obs,
                out=args.out,
                seed=args.seed,
                ppc_n=args.ppc_n,
                workers=args.workers,
                dry_run=args.dry_run,
            )
        )
    elif args.cmd == "report":
        import logging
        import sys

        logging.getLogger("conduction_lens").addHandler(logging.StreamHandler(sys.stdout))
        logging.getLogger("conduction_lens").setLevel(logging.INFO)
        pipeline.report(args.out)


if __name__ == "__main__":
    main()
