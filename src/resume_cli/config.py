from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

from .errors import ResumeCLIError

DEFAULT_CONFIG_PATH = Path(".env")
DEFAULT_MODEL = "deepseek-flash"
DEFAULT_BASE_URL = "https://api.deepseek.com"


@dataclass(frozen=True)
class DeepSeekConfig:
    api_key: str
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL


def load_deepseek_config(path: Path = DEFAULT_CONFIG_PATH) -> DeepSeekConfig:
    if not path.exists():
        raise ResumeCLIError(
            f"配置文件不存在：{path}；请复制 .env.example 为 .env 并填写 API Key"
        )
    if not path.is_file():
        raise ResumeCLIError(f"配置路径不是文件：{path}")

    try:
        data = dotenv_values(path)
    except (OSError, UnicodeError) as exc:
        raise ResumeCLIError(f"配置文件无法读取：{exc}") from exc

    api_key = data.get("DEEPSEEK_API_KEY")
    if not isinstance(api_key, str) or not api_key.strip():
        raise ResumeCLIError("配置项 DEEPSEEK_API_KEY 不能为空")

    model = data.get("DEEPSEEK_MODEL", DEFAULT_MODEL)
    if not isinstance(model, str) or not model.strip():
        raise ResumeCLIError("配置项 DEEPSEEK_MODEL 必须是非空字符串")

    base_url = data.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)
    if not isinstance(base_url, str) or not base_url.strip():
        raise ResumeCLIError("配置项 DEEPSEEK_BASE_URL 必须是非空字符串")

    return DeepSeekConfig(
        api_key=api_key.strip(),
        model=model.strip(),
        base_url=base_url.strip().rstrip("/"),
    )
