import json
from types import SimpleNamespace

from resume_cli.config import DEFAULT_BASE_URL
from resume_cli.deepseek import DeepSeekResumeAnalyzer
from resume_cli.models import ResumeData


class FakeResponses:
    def __init__(self) -> None:
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(
            status="completed",
            output_text=json.dumps(
                {
                    "name": "Alice Chen",
                    "phone": "",
                    "email": "alice@example.com",
                    "city": "Shanghai",
                    "professional_summary": "具备 Python 后端开发经验。",
                    "personal_advantages": ["具有 Python 项目经验"],
                    "current_title": "Backend Engineer",
                    "years_of_experience": "3年",
                    "job_intention": "",
                    "education": [],
                    "work_experience": [],
                    "project_experience": [],
                    "skills": ["Python"],
                    "certifications": [],
                    "languages": [],
                }
            ),
            incomplete_details=None,
            error=None,
        )


class FakeClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def test_deepseek_uses_config_file_and_json_schema(monkeypatch, tmp_path) -> None:
    client = FakeClient()
    client_config = {}
    config_path = tmp_path / ".env"
    config_path.write_text(
        """DEEPSEEK_API_KEY=test-key
DEEPSEEK_MODEL=deepseek-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
""",
        encoding="utf-8",
    )

    def make_client(**kwargs):
        client_config.update(kwargs)
        return client

    monkeypatch.setattr("resume_cli.deepseek.OpenAI", make_client)

    result = DeepSeekResumeAnalyzer(config_path).extract(
        "Alice Chen\nalice@example.com\nPython"
    )

    assert client_config == {
        "api_key": "test-key",
        "base_url": DEFAULT_BASE_URL,
    }
    assert client.responses.request["model"] == "deepseek-flash"
    assert client.responses.request["text"]["format"]["type"] == "json_schema"
    schema = client.responses.request["text"]["format"]["schema"]
    assert "work_experience" in schema["properties"]
    assert "project_experience" in schema["properties"]
    assert "personal_advantages" in schema["properties"]
    assert result.email == "alice@example.com"


def test_resume_data_removes_work_item_without_employment_evidence() -> None:
    data = ResumeData.model_validate(
        {
            "name": "Alice Chen",
            "phone": "",
            "email": "",
            "city": "",
            "professional_summary": "",
            "personal_advantages": [],
            "current_title": "Project A",
            "years_of_experience": "",
            "job_intention": "",
            "education": [],
            "work_experience": [
                {
                    "company": "",
                    "title": "",
                    "location": "",
                    "start_time": "",
                    "end_time": "",
                    "responsibilities": [],
                    "achievements": [],
                    "technologies": ["Python"],
                }
            ],
            "project_experience": [],
            "skills": ["Python"],
            "certifications": [],
            "languages": [],
        }
    )

    assert data.work_experience == []
    assert data.current_title == ""
