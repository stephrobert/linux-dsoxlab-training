#!/usr/bin/env python3
"""Génère la table des labs (id, titre, niveau, runtime, guide) dans les README.

Source de vérité : l'ordre des sections de meta.yml + chaque labs/**/lab.yaml
(et lab.fr.yaml pour le titre français). Écrit entre les marqueurs
<!-- LABS:START --> et <!-- LABS:END --> de README.md et README.fr.md.

Usage :
    python3 scripts/gen_catalog.py           # régénère les README
    python3 scripts/gen_catalog.py --check    # échoue (exit 1) si un README est périmé
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "meta.yml"
START, END = "<!-- LABS:START -->", "<!-- LABS:END -->"

# En-têtes de colonnes par langue.
HEAD = {
    "en": ("Lab (id)", "Title", "Level", "Certif", "Runtime", "Companion guide"),
    "fr": ("Lab (id)", "Titre", "Niveau", "Certif", "Runtime", "Guide compagnon"),
}
SECTION_LABEL = {"en": "Section", "fr": "Section"}


def _runtime_label(lab: dict) -> str:
    rt = lab.get("runtime") or {}
    return str(rt.get("type", "shell"))


def _rows_by_section() -> list[tuple[str, str, list[dict]]]:
    """Retourne [(section_id, section_title, [lab_dict, ...]), ...] dans l'ordre meta.yml."""
    meta = yaml.safe_load(META.read_text(encoding="utf-8"))
    out: list[tuple[str, str, list[dict]]] = []
    for section in meta.get("sections", []):
        labs: list[dict] = []
        for rel in section.get("labs") or []:
            lab_dir = ROOT / "labs" / rel
            lab_yaml = lab_dir / "lab.yaml"
            if not lab_yaml.exists():
                continue
            lab = yaml.safe_load(lab_yaml.read_text(encoding="utf-8")) or {}
            fr_yaml = lab_dir / "lab.fr.yaml"
            lab["_title_fr"] = lab.get("title", "")
            if fr_yaml.exists():
                fr = yaml.safe_load(fr_yaml.read_text(encoding="utf-8")) or {}
                lab["_title_fr"] = fr.get("title", lab.get("title", ""))
            labs.append(lab)
        if labs:
            out.append((section.get("id", ""), section.get("title", ""), labs))
    return out


def _certif_cell(lab: dict) -> str:
    """Rend les certifications visées (certification_tags), ex. « RHCSA · LFCS »."""
    tags = lab.get("certification_tags") or []
    if not tags:
        return "—"
    return " · ".join(str(t).upper() for t in tags)


def _guide_cell(lab: dict, lang: str) -> str:
    url = lab.get("doc_url", "")
    if not url:
        return "—"
    label = "guide" if lang == "en" else "guide"
    return f"[{label}]({url})"


def _table(lang: str) -> str:
    head = HEAD[lang]
    lines: list[str] = []
    for _sid, stitle, labs in _rows_by_section():
        lines.append(f"### {stitle}")
        lines.append("")
        lines.append("| " + " | ".join(head) + " |")
        lines.append("|" + "|".join(["---"] * len(head)) + "|")
        for lab in labs:
            title = lab["_title_fr"] if lang == "fr" else lab.get("title", "")
            lines.append(
                "| `{id}` | {title} | {level} | {certif} | {rt} | {guide} |".format(
                    id=lab.get("id", ""),
                    title=title,
                    level=lab.get("level", ""),
                    certif=_certif_cell(lab),
                    rt=_runtime_label(lab),
                    guide=_guide_cell(lab, lang),
                )
            )
        lines.append("")
    total = sum(len(labs) for _s, _t, labs in _rows_by_section())
    caption = (
        f"_{total} labs — table générée par `scripts/gen_catalog.py`._"
        if lang == "en"
        else f"_{total} labs — table générée par `scripts/gen_catalog.py`._"
    )
    lines.append(caption)
    return "\n".join(lines)


def _rendered(path: Path, block: str) -> str:
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"marqueurs absents dans {path}")
    pre = text.split(START)[0]
    post = text.split(END)[1]
    return f"{pre}{START}\n{block}\n{END}{post}"


TARGETS = {"README.md": "en", "README.fr.md": "fr"}


def _check() -> int:
    stale = []
    for name, lang in TARGETS.items():
        path = ROOT / name
        if path.read_text(encoding="utf-8") != _rendered(path, _table(lang)):
            stale.append(name)
    if stale:
        print(
            "Catalogue périmé dans : "
            + ", ".join(stale)
            + "\nLance `python3 scripts/gen_catalog.py` puis recommite.",
            file=sys.stderr,
        )
        return 1
    print("catalogue à jour")
    return 0


def _write() -> None:
    for name, lang in TARGETS.items():
        path = ROOT / name
        path.write_text(_rendered(path, _table(lang)), encoding="utf-8")
    print("catalogue régénéré dans README.md et README.fr.md")


def main() -> None:
    if "--check" in sys.argv[1:]:
        raise SystemExit(_check())
    _write()


if __name__ == "__main__":
    main()
