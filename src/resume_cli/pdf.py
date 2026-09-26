from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .errors import ResumeCLIError


def extract_pdf_text(path: Path) -> str:
    """Validate and extract text from a local PDF file."""
    if not path.exists():
        raise ResumeCLIError(f"PDF 文件不存在：{path}")
    if not path.is_file():
        raise ResumeCLIError(f"PDF 路径不是文件：{path}")
    if path.suffix.lower() != ".pdf":
        raise ResumeCLIError(f"文件不是 PDF：{path}")

    try:
        with path.open("rb") as file:
            if file.read(5) != b"%PDF-":
                raise ResumeCLIError(f"文件内容不是有效的 PDF：{path}")
            file.seek(0)
            reader = PdfReader(file, strict=False)
            if reader.is_encrypted and reader.decrypt("") == 0:
                raise ResumeCLIError("PDF 已加密，无法读取；请先移除密码")

            pages: list[str] = []
            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    pages.append(page.extract_text() or "")
                except Exception as exc:
                    raise ResumeCLIError(
                        f"PDF 第 {page_number} 页文本提取失败：{exc}"
                    ) from exc
    except ResumeCLIError:
        raise
    except (OSError, PdfReadError, ValueError) as exc:
        raise ResumeCLIError(f"PDF 无法读取：{exc}") from exc

    text = "\n\n".join(page.strip() for page in pages if page.strip()).strip()
    if not text:
        raise ResumeCLIError("PDF 文本为空；文件可能是扫描件，当前版本暂不支持 OCR")
    return text
