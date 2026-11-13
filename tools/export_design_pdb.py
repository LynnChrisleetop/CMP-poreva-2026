#!/usr/bin/env python3
"""把已核对的 target_observed.cif 导出为设计软件可读的 PDB。

不补缺口，不改残基，不重建侧链。只保留指定链上已有原子。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from Bio.PDB import MMCIFParser, PDBIO, Select


class ChainSelect(Select):
    def __init__(self, chains: set[str]) -> None:
        self.chains = chains

    def accept_chain(self, chain) -> bool:
        return chain.id in self.chains


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cif", type=Path, required=True)
    parser.add_argument("--pdb", type=Path, required=True)
    parser.add_argument("--chains", default="A,B,C")
    parser.add_argument("--note", type=Path, required=True)
    args = parser.parse_args()

    chains = {part.strip() for part in args.chains.split(",") if part.strip()}
    structure = MMCIFParser(QUIET=True).get_structure("target", str(args.cif))
    model = next(structure.get_models())
    present = [chain.id for chain in model if chain.id in chains]
    missing = sorted(chains - set(present))
    if missing:
        raise SystemExit(f"CIF 中缺少链：{', '.join(missing)}")

    args.pdb.parent.mkdir(parents=True, exist_ok=True)
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(args.pdb), ChainSelect(chains))

    counts = {}
    for chain in model:
        if chain.id not in chains:
            continue
        residues = [res for res in chain if res.id[0] == " "]
        counts[chain.id] = len(residues)

    note = {
        "source_cif": str(args.cif),
        "pdb": str(args.pdb),
        "chains": present,
        "observed_residues_per_chain": counts,
        "policy": "未补缺口，未改序列，未加氢。",
    }
    args.note.write_text(json.dumps(note, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(note, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
