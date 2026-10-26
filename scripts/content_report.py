"""Create a readable, read-only status report for Alicia content assets."""
import json
from pathlib import Path

GENERATED_DIR = Path("content/generated")
SELECTED_DIR = Path("content/selected")
CAPTIONS_DIR = Path("content/captions")
QUEUE_DIR = Path("content/queue")
OUTPUT_PATH = Path("reports/content_status.md")


def _read_json(path, warnings, kind):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("expected a JSON object")
        return value
    except (OSError, json.JSONDecodeError, ValueError) as error:
        warnings.append(f"{kind} file `{path.as_posix()}` could not be read: {error}")
        return None


def build_report(generated_dir=GENERATED_DIR, selected_dir=SELECTED_DIR,
                 captions_dir=CAPTIONS_DIR, queue_dir=QUEUE_DIR):
    generated = {p.name for p in generated_dir.glob("*.png") if p.is_file()}
    selected = {p.name for p in selected_dir.glob("*.png") if p.is_file()}
    warnings = []
    captions = {}
    for path in sorted(captions_dir.glob("*.json")):
        record = _read_json(path, warnings, "Caption")
        if record is not None:
            image = record.get("image")
            if isinstance(image, str) and image:
                captions[image] = record

    queue = {}
    for path in sorted(queue_dir.glob("*.json")):
        record = _read_json(path, warnings, "Queue")
        if record is not None:
            image = record.get("image")
            if isinstance(image, str) and image:
                queue[image] = record

    images = sorted(generated | selected | set(captions) | set(queue))
    lines = [
        "# Alicia content status",
        "",
        "Read-only inventory. This report never publishes posts or makes Metricool/Instagram API calls.",
        "",
        f"- Generated PNGs: **{len(generated)}**",
        f"- Selected PNGs: **{len(selected)}**",
        f"- Caption records: **{len(captions)}**",
        f"- Queue records: **{len(queue)}**",
        "",
        "| Image | Generated | Selected | Caption status | Queue status | Scheduled (UTC) |",
        "|---|---:|---:|---|---|---|",
    ]
    if not images:
        lines.append("| _No content files found yet_ | — | — | — | — | — |")
    for image in images:
        caption_record = captions.get(image)
        queue_record = queue.get(image)
        caption_status = caption_record.get("status", "status missing") if caption_record else "missing"
        queue_status = queue_record.get("status", "status missing") if queue_record else "missing"
        scheduled = queue_record.get("scheduled_at_utc", "—") if queue_record else "—"
        lines.append(
            f"| `{image}` | {'yes' if image in generated else 'no'} | "
            f"{'yes' if image in selected else 'no'} | {caption_status} | "
            f"{queue_status} | {scheduled} |"
        )

    if warnings:
        lines.extend(["", "## Data warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
    lines.extend([
        "",
        "## Safety",
        "",
        "- This report is read-only and never performs Metricool or Instagram API operations.",
        "- The Metricool sync workflow only submits queue entries with `publishing_enabled: true`.",
        "",
    ])
    return "\n".join(lines)


def main():
    report = build_report()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"Content report written to {OUTPUT_PATH}")
    print(report)


if __name__ == "__main__":
    main()
