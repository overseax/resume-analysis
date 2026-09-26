import json
from pathlib import Path

from reportlab.pdfgen import canvas
from typer.testing import CliRunner

from resume_cli.cli import app

runner = CliRunner()


def make_pdf(path: Path, lines: list[str]) -> None:
    pdf = canvas.Canvas(str(path))
    y = 800
    for line in lines:
        pdf.drawString(50, y, line)
        y -= 24
    pdf.save()


def test_parse_reports_missing_file() -> None:
    result = runner.invoke(app, ["parse", "missing.pdf"])

    assert result.exit_code == 1
    assert "PDF 文件不存在" in result.stderr


def test_parse_extracts_pdf_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "resume.pdf"
    make_pdf(pdf_path, ["Alice Chen", "alice@example.com", "Python FastAPI"])

    result = runner.invoke(app, ["parse", str(pdf_path)])

    assert result.exit_code == 0
    assert "Alice Chen" in result.stdout
    assert "alice@example.com" in result.stdout


def test_extract_mock_returns_valid_json(tmp_path: Path) -> None:
    pdf_path = tmp_path / "resume.pdf"
    make_pdf(pdf_path, ["Alice Chen", "alice@example.com", "Python FastAPI Docker"])

    result = runner.invoke(app, ["extract", str(pdf_path), "--mock"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["name"] == "Alice Chen"
    assert data["email"] == "alice@example.com"
    assert "Python" in data["skills"]
    assert "professional_summary" in data
    assert data["personal_advantages"] == []
    assert data["work_experience"] == []
    assert data["project_experience"] == []


def test_score_rejects_empty_jd(tmp_path: Path) -> None:
    pdf_path = tmp_path / "resume.pdf"
    jd_path = tmp_path / "jd.txt"
    make_pdf(pdf_path, ["Alice Chen", "Python"])
    jd_path.write_text("", encoding="utf-8")

    result = runner.invoke(
        app, ["score", str(pdf_path), "--jd", str(jd_path), "--mock"]
    )

    assert result.exit_code == 1
    assert "JD 文件为空" in result.stderr
