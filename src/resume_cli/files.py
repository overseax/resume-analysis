from pathlib import Path

from .errors import ResumeCLIError


def read_jd(path: Path) -> str:
    if not path.exists():
        raise ResumeCLIError(f"JD 文件不存在：{path}")
    if not path.is_file():
        raise ResumeCLIError(f"JD 路径不是文件：{path}")

    try:
        text = path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ResumeCLIError("JD 文件必须是 UTF-8 编码的文本文件") from exc
    except OSError as exc:
        raise ResumeCLIError(f"JD 文件无法读取：{exc}") from exc

    if not text:
        raise ResumeCLIError("JD 文件为空")
    return text


def write_output(path: Path, content: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ResumeCLIError(f"结果文件无法写入：{exc}") from exc
