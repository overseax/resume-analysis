import json
import logging
from pathlib import Path
from typing import Annotated

import typer

from .config import DEFAULT_CONFIG_PATH
from .deepseek import DeepSeekResumeAnalyzer
from .errors import ResumeCLIError
from .files import read_jd, write_output
from .mock import mock_extract, mock_score
from .pdf import extract_pdf_text

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="resume-cli",
    help="读取 PDF 简历、提取结构化信息并进行 JD 匹配评分。",
    no_args_is_help=True,
)


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )


def _emit(content: str, output: Path | None) -> None:
    if output:
        write_output(output, content + ("" if content.endswith("\n") else "\n"))
        typer.echo(f"结果已保存到：{output}", err=True)
    else:
        typer.echo(content)


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def _fail(exc: ResumeCLIError) -> None:
    typer.echo(f"错误：{exc}", err=True)
    raise typer.Exit(code=1)


@app.command("parse")
def parse_command(
    pdf_path: Annotated[Path, typer.Argument(help="本地 PDF 简历路径")],
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="保存文本结果")
    ] = None,
) -> None:
    """从 PDF 简历中提取原始文本。"""
    try:
        _emit(extract_pdf_text(pdf_path), output)
    except ResumeCLIError as exc:
        _fail(exc)


@app.command("extract")
def extract_command(
    pdf_path: Annotated[Path, typer.Argument(help="本地 PDF 简历路径")],
    mock: Annotated[bool, typer.Option(help="使用本地规则演示，不调用 AI")] = False,
    config: Annotated[
        Path, typer.Option("--config", "-c", help="DeepSeek .env 配置文件")
    ] = DEFAULT_CONFIG_PATH,
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="保存 JSON 结果")
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="显示运行日志")
    ] = False,
) -> None:
    """使用 AI 从简历中提取结构化信息。"""
    _configure_logging(verbose)
    try:
        text = extract_pdf_text(pdf_path)
        logger.info("已提取 %d 个字符", len(text))
        result = (
            mock_extract(text) if mock else DeepSeekResumeAnalyzer(config).extract(text)
        )
        _emit(_json(result.model_dump()), output)
    except ResumeCLIError as exc:
        _fail(exc)


@app.command("score")
def score_command(
    pdf_path: Annotated[Path, typer.Argument(help="本地 PDF 简历路径")],
    jd_path: Annotated[Path, typer.Option("--jd", help="UTF-8 JD 文本文件路径")],
    mock: Annotated[bool, typer.Option(help="使用本地规则演示，不调用 AI")] = False,
    config: Annotated[
        Path, typer.Option("--config", "-c", help="DeepSeek .env 配置文件")
    ] = DEFAULT_CONFIG_PATH,
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="保存 JSON 结果")
    ] = None,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="显示运行日志")
    ] = False,
) -> None:
    """使用 AI 对简历与岗位描述进行匹配评分。"""
    _configure_logging(verbose)
    try:
        text = extract_pdf_text(pdf_path)
        jd_text = read_jd(jd_path)
        logger.info("已读取简历 %d 字符、JD %d 字符", len(text), len(jd_text))
        result = (
            mock_score(text, jd_text)
            if mock
            else DeepSeekResumeAnalyzer(config).score(text, jd_text)
        )
        _emit(_json(result.model_dump()), output)
    except ResumeCLIError as exc:
        _fail(exc)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
