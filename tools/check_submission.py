#!/usr/bin/env python3
"""检查 Poreva Open 序列文件。

默认按 2026-11-03 中文报名页（--rules form）。
--rules guide 改按同一天抽出的《平台使用说明》：蛋白、纳米抗体和 scFv 是单链，
scFv 含 G4S linker；IgG1 配对可变区用英文冒号，每条链 40–250。
两套规则目前并不一致。脚本不判断结合、pH 或细胞功能。
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from dataclasses import dataclass
from pathlib import Path

EXPECTED_HEADER = ("序号", "序列名称", "序列")
STANDARD_AA = set("ACDEFGHIKLMNPQRSTVWY")
FORM_MAX_LENGTH = 300
GUIDE_MIN_LENGTH = 40
GUIDE_MAX_LENGTH = 250
REQUIRED_ROWS = 24
FORM_PAIRED = {"scfv", "igg1"}

MOLECULE_ALIASES = {
    "protein": "protein",
    "蛋白": "protein",
    "vhh": "vhh",
    "纳米抗体": "vhh",
    "nanobody": "vhh",
    "scfv": "scfv",
    "scfv抗体": "scfv",
    "igg1": "igg1",
    "常规igg1配对可变区": "igg1",
}

MOLECULE_LABELS = {
    "protein": "蛋白",
    "vhh": "纳米抗体",
    "scfv": "scFv",
    "igg1": "常规IgG1配对可变区",
}


@dataclass
class Issue:
    where: str
    message: str


EXPRESSION_ALIASES = {
    "hek293": "HEK293",
    "mammalian": "HEK293",
    "哺乳动物": "HEK293",
    "hek293表达系统": "HEK293",
    "cell_free": "cell_free",
    "cell-free": "cell_free",
    "无细胞": "cell_free",
    "无细胞表达系统": "cell_free",
}


def canonical_molecule_type(value: str) -> str | None:
    return MOLECULE_ALIASES.get(value.strip().casefold())


def canonical_expression(value: str | None) -> str | None:
    if value is None or value.strip() == "":
        return None
    return EXPRESSION_ALIASES.get(value.strip().casefold())


def check_chain(chain: str, label: str, where: str, issues: list[Issue]) -> None:
    if chain == "":
        issues.append(Issue(where, f"{label}为空"))
        return
    lowered = sorted({ch for ch in chain if ch.isalpha() and ch == ch.lower() and ch.upper() in STANDARD_AA})
    if lowered:
        issues.append(Issue(where, f"{label}含小写字母 {''.join(lowered)}，页面要求标准氨基酸字母"))
    bad = sorted({ch for ch in chain if ch not in STANDARD_AA and not (ch.isalpha() and ch.upper() in STANDARD_AA)})
    if bad:
        issues.append(Issue(where, f"{label}含非标准氨基酸或非法字符：{''.join(bad)}"))


def clean_header_name(name: str | None) -> str:
    return (name or "").strip().lstrip("\ufeff")


def check_text(
    text: str,
    molecule_type: str,
    rules: str = "form",
    expression_system: str | None = None,
) -> tuple[list[Issue], list[Issue]]:
    issues: list[Issue] = []
    warnings: list[Issue] = []
    if rules not in {"form", "guide"}:
        return [Issue("文件", "规则来源须是 form 或 guide")], []
    expression = canonical_expression(expression_system)
    if expression_system and expression is None:
        return [Issue("文件", "表达系统须是 HEK293 或 cell_free")], []
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        return [Issue("文件", "没有表头")], []

    header = tuple(clean_header_name(name) for name in reader.fieldnames)
    if header != EXPECTED_HEADER:
        shown = ",".join(header)
        return [Issue("文件", f"表头应为 序号,序列名称,序列，当前为 {shown}")], []

    rows: list[dict[str, str]] = []
    for raw in reader:
        cleaned = {clean_header_name(key): (value or "") for key, value in raw.items() if key is not None}
        rows.append({key: cleaned.get(key, "") for key in EXPECTED_HEADER})

    if len(rows) != REQUIRED_ROWS:
        issues.append(Issue("文件", f"数据行数为 {len(rows)}，页面要求恰好 {REQUIRED_ROWS} 条"))

    paired = molecule_type in FORM_PAIRED if rules == "form" else molecule_type == "igg1"
    scfv_without_g4s = 0
    names: dict[str, int] = {}
    folded_names: dict[str, str] = {}
    sequences: dict[str, int] = {}
    parsed_ranks: list[int] = []
    ranks_complete = True

    for index, row in enumerate(rows, start=1):
        where = f"第{index}条"
        rank_text = row["序号"].strip()
        name_raw = row["序列名称"]
        name = name_raw.strip()
        raw_sequence = row["序列"]

        if rank_text == "":
            issues.append(Issue(where, "序号为空"))
            ranks_complete = False
        else:
            try:
                rank = int(rank_text)
            except ValueError:
                issues.append(Issue(where, f"序号不是整数：{rank_text}"))
                ranks_complete = False
            else:
                parsed_ranks.append(rank)
                if rank < 1 or rank > REQUIRED_ROWS:
                    issues.append(Issue(where, f"序号 {rank} 不在 1–{REQUIRED_ROWS}"))

        if name == "":
            issues.append(Issue(where, "序列名称为空"))
        elif name_raw != name or any(ch.isspace() for ch in name):
            issues.append(Issue(where, "序列名称含首尾或内部空白"))
        elif rules == "guide" and len(name) > 50:
            issues.append(Issue(where, f"序列名称长度为 {len(name)}，平台使用说明要求不超过 50"))
        else:
            names[name] = names.get(name, 0) + 1
            previous = folded_names.get(name.casefold())
            if previous is not None and previous != name:
                issues.append(Issue(where, f"序列名称与 {previous} 只有大小写不同"))
            else:
                folded_names.setdefault(name.casefold(), name)

        if raw_sequence.strip() == "":
            issues.append(Issue(where, "序列为空"))
            continue
        if raw_sequence != raw_sequence.strip() or any(ch.isspace() for ch in raw_sequence):
            issues.append(Issue(where, "序列含空白，提交前去掉空格和换行"))

        sequence = "".join(raw_sequence.split())
        sequences[sequence] = sequences.get(sequence, 0) + 1
        if "：" in sequence:
            issues.append(Issue(where, "发现中文冒号，配对序列须使用一个英文冒号"))

        colon_count = sequence.count(":")
        if paired:
            if colon_count != 1:
                if rules == "guide":
                    issues.append(Issue(where, "平台使用说明要求 IgG1 配对可变区写成 VH:VL，且只有一个英文冒号"))
                else:
                    issues.append(Issue(where, "报名表要求 scFv 与 IgG1 写成 VH:VL，且只有一个英文冒号、不加 linker"))
            else:
                vh, vl = sequence.split(":")
                check_chain(vh, "VH", where, issues)
                check_chain(vl, "VL", where, issues)
                if vh != "" and vl != "":
                    total = len(vh) + len(vl)
                    if rules == "guide":
                        for label, chain in (("VH", vh), ("VL", vl)):
                            if len(chain) < GUIDE_MIN_LENGTH or len(chain) > GUIDE_MAX_LENGTH:
                                issues.append(Issue(where, f"{label}长度为 {len(chain)}，平台使用说明要求每条链 40–250"))
                        if total > FORM_MAX_LENGTH:
                            warnings.append(Issue(where, f"VH+VL 合计 {total}。使用说明按每条链计，报名表还写了合计不超过 300"))
                    elif total > FORM_MAX_LENGTH:
                        issues.append(Issue(where, f"VH+VL 长度为 {total}，报名表要求不超过 {FORM_MAX_LENGTH}"))
        else:
            if colon_count or "：" in sequence:
                if rules == "guide" and molecule_type == "scfv":
                    issues.append(Issue(where, "平台使用说明要求 scFv 写成含 G4S linker 的单链，不使用冒号"))
                else:
                    issues.append(Issue(where, "蛋白、纳米抗体以及使用说明中的 scFv 须提交单条序列，不能含冒号"))
            chain = sequence.replace("：", "")
            check_chain(chain, "序列", where, issues)
            length = len(chain.replace(":", ""))
            if rules == "guide":
                if length < GUIDE_MIN_LENGTH or length > GUIDE_MAX_LENGTH:
                    issues.append(Issue(where, f"序列长度为 {length}，平台使用说明要求 40–250"))
                if molecule_type == "scfv" and "GGGGS" not in chain:
                    scfv_without_g4s += 1
            elif length > FORM_MAX_LENGTH:
                issues.append(Issue(where, f"序列长度为 {length}，报名表要求不超过 {FORM_MAX_LENGTH}"))

    if ranks_complete and len(parsed_ranks) == REQUIRED_ROWS:
        if set(parsed_ranks) != set(range(1, REQUIRED_ROWS + 1)):
            missing = [str(n) for n in range(1, REQUIRED_ROWS + 1) if parsed_ranks.count(n) == 0]
            duplicated = [str(n) for n in range(1, REQUIRED_ROWS + 1) if parsed_ranks.count(n) > 1]
            if missing:
                issues.append(Issue("文件", "缺少序号：" + ", ".join(missing)))
            if duplicated:
                issues.append(Issue("文件", "重复序号：" + ", ".join(duplicated)))
        elif parsed_ranks != list(range(1, REQUIRED_ROWS + 1)):
            issues.append(Issue("文件", "序号须按 1 到 24 从上到下排列，1 为最推荐"))

    for name, count in sorted(names.items()):
        if count > 1:
            issues.append(Issue("文件", f"序列名称重复：{name}"))
    for sequence, count in sorted(sequences.items()):
        if count > 1 and sequence != "":
            issues.append(Issue("文件", f"序列重复 {count} 次：{sequence[:40]}"))
    if molecule_type == "igg1" and expression == "cell_free":
        issues.append(Issue("文件", "赛题页写明配对 VH/VL 只能使用哺乳动物（HEK293）表达系统"))
    if rules == "form" and molecule_type == "scfv":
        warnings.append(Issue("文件", "报名表要求 scFv 写成 VH:VL 且不加 linker；平台使用说明要求 scFv 是含 G4S linker 的单链。两份文件还没有对齐"))
    if scfv_without_g4s:
        warnings.append(Issue("文件", f"{scfv_without_g4s} 条 scFv 没有看到 GGGGS。使用说明推荐 GGGGS 重复作为 linker"))
    return issues, warnings


def read_submission(path: Path) -> str:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        raise ValueError("Excel 请先另存为 UTF-8 CSV，再用本脚本检查")
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("无法按 UTF-8 读取。请把文件另存为 UTF-8 CSV") from exc


def render(
    path_label: str,
    molecule_type: str,
    rules: str,
    issues: list[Issue],
    warnings: list[Issue],
) -> str:
    label = MOLECULE_LABELS[molecule_type]
    lines = [f"文件：{path_label}", f"分子类型：{label}", f"规则来源：{rules}"]
    if issues:
        lines.append(f"结果：未通过（{len(issues)} 项）")
        for issue in issues:
            lines.append(f"- {issue.where}：{issue.message}")
    else:
        lines.append("结果：通过这一套规则的格式检查")
        if rules == "form" and molecule_type in FORM_PAIRED:
            lines.append("仍需人工确认：英文冒号两侧分别是 VH 和 VL。")
        lines.append("格式通过不代表会被遴选进湿实验。")
    for warning in warnings:
        lines.append(f"注意 {warning.where}：{warning.message}")
    return "\n".join(lines)


def make_csv(sequences: list[str], ranks: list[int] | None = None, names: list[str] | None = None) -> str:
    lines = ["序号,序列名称,序列"]
    for index, sequence in enumerate(sequences, start=1):
        rank = index if ranks is None else ranks[index - 1]
        name = f"seq{index:02d}" if names is None else names[index - 1]
        lines.append(f"{rank},{name},{sequence}")
    return "\n".join(lines) + "\n"


def run_self_test() -> int:
    protein_ok = ["A" * (11 + i) for i in range(24)]
    paired_ok = ["A" * 20 + ":" + "C" * (20 + i) for i in range(24)]
    guide_protein = ["A" * (40 + i) for i in range(24)]
    guide_scfv = ["A" * (20 + i) + "GGGGSGGGGSGGGGS" + "C" * 20 for i in range(24)]
    guide_igg = ["A" * 50 + ":" + "C" * (50 + i) for i in range(24)]
    cases: list[tuple[str, str, str, bool, str]] = [
        ("蛋白合法", "protein", make_csv(protein_ok), True, "form"),
        ("scFv 合法", "scfv", make_csv(paired_ok), True, "form"),
        ("IgG1 合法", "igg1", make_csv(paired_ok), True, "form"),
        ("蛋白含冒号", "protein", make_csv(paired_ok), False, "form"),
        ("纳米抗体缺一条", "vhh", make_csv(protein_ok[:23]), False, "form"),
        ("scFv 没有冒号", "scfv", make_csv(protein_ok), False, "form"),
        ("超长", "protein", make_csv(["A" * 301] + protein_ok[1:]), False, "form"),
        ("配对超长", "scfv", make_csv(["A" * 150 + ":" + "C" * 151] + paired_ok[1:]), False, "form"),
        ("两个冒号", "scfv", make_csv(["AAA:CCC:DDD"] + paired_ok[1:]), False, "form"),
        ("空 VL", "scfv", make_csv(["AAA:"] + paired_ok[1:]), False, "form"),
        ("小写", "protein", make_csv(["AaaAAAAAAAA"] + protein_ok[1:]), False, "form"),
        ("非法字符", "protein", make_csv(["AAA1AAAAAAAA"] + protein_ok[1:]), False, "form"),
        ("中文冒号", "scfv", make_csv(["AAAA：CCCC"] + paired_ok[1:]), False, "form"),
        ("序号乱序", "protein", make_csv(protein_ok, ranks=[2, 1] + list(range(3, 25))), False, "form"),
        ("重名", "protein", make_csv(protein_ok, names=["same"] * 2 + [f"seq{i:02d}" for i in range(3, 25)]), False, "form"),
        ("重复序列", "protein", make_csv([protein_ok[0], protein_ok[0]] + protein_ok[2:]), False, "form"),
        ("错误表头", "protein", "id,name,seq\n" + "\n".join(f"{i},seq{i:02d},{'A' * 12}" for i in range(1, 25)) + "\n", False, "form"),
        ("UTF-8 BOM", "protein", "\ufeff" + make_csv(protein_ok), True, "form"),
        ("使用说明蛋白", "protein", make_csv(guide_protein), True, "guide"),
        ("使用说明过短", "protein", make_csv(["A" * 39] + guide_protein[1:]), False, "guide"),
        ("使用说明过长", "protein", make_csv(["A" * 251] + guide_protein[1:]), False, "guide"),
        ("使用说明 scFv", "scfv", make_csv(guide_scfv), True, "guide"),
        ("使用说明 scFv 含冒号", "scfv", make_csv(paired_ok), False, "guide"),
        ("使用说明 IgG1", "igg1", make_csv(guide_igg), True, "guide"),
        ("使用说明 IgG1 链过短", "igg1", make_csv(["A" * 30 + ":" + "C" * 50] + guide_igg[1:]), False, "guide"),
    ]

    failed = 0
    for name, molecule_type, text, expect_pass, rules in cases:
        issues, _warnings = check_text(text, molecule_type, rules=rules)
        passed = not issues
        if passed != expect_pass:
            failed += 1
            print(f"自测失败：{name}，期望通过={expect_pass}，实际问题数={len(issues)}", file=sys.stderr)
            for issue in issues:
                print(f"  {issue.where}：{issue.message}", file=sys.stderr)
    if failed:
        print(f"自测未通过：{failed} 项", file=sys.stderr)
        return 3
    print(f"自测通过：{len(cases)} 项")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查 Poreva Open 序列 CSV 的报名页格式")
    parser.add_argument("file", nargs="?", type=Path, help="UTF-8 CSV 路径")
    parser.add_argument("--molecule-type", help="protein、vhh、scfv、igg1，或报名页上的中文名称")
    parser.add_argument("--rules", choices=["form", "guide"], default="form", help="form 为中文报名页，guide 为平台使用说明")
    parser.add_argument("--expression-system", help="HEK293 或 cell_free。配对 VH/VL 选无细胞时会报错")
    parser.add_argument("--self-test", action="store_true", help="用合成序列检查脚本自身")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.self_test:
        return run_self_test()
    if args.file is None or args.molecule_type is None:
        print(
            "用法：python3 tools/check_submission.py <文件.csv> --molecule-type protein|vhh|scfv|igg1 [--rules form|guide]",
            file=sys.stderr,
        )
        return 2
    molecule_type = canonical_molecule_type(args.molecule_type)
    if molecule_type is None:
        print("分子类型须是 protein、vhh、scfv、igg1，或对应的报名页中文名称", file=sys.stderr)
        return 2
    if args.expression_system and canonical_expression(args.expression_system) is None:
        print("表达系统须是 HEK293 或 cell_free", file=sys.stderr)
        return 2
    try:
        text = read_submission(args.file)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    issues, warnings = check_text(
        text,
        molecule_type,
        rules=args.rules,
        expression_system=args.expression_system,
    )
    print(render(str(args.file), molecule_type, args.rules, issues, warnings))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
