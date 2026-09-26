import re

from .models import Education, ProjectExperience, ResumeData, ScoreResult

SKILL_TERMS = (
    "Python",
    "Golang",
    "Go",
    "Java",
    "JavaScript",
    "TypeScript",
    "React",
    "Vue",
    "Next.js",
    "FastAPI",
    "Django",
    "Flask",
    "Node.js",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "Redis",
    "Docker",
    "Kubernetes",
    "AWS",
    "Git",
    "OpenAI",
    "DeepSeek",
    "LLM",
)

CITIES = (
    "北京",
    "Beijing",
    "上海",
    "Shanghai",
    "深圳",
    "Shenzhen",
    "广州",
    "Guangzhou",
    "杭州",
    "Hangzhou",
    "成都",
    "武汉",
    "南京",
    "苏州",
    "西安",
    "Hong Kong",
    "Singapore",
)


def _first_match(pattern: str, text: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    return match.group(0).strip() if match else ""


def mock_extract(resume_text: str) -> ResumeData:
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    email = _first_match(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", resume_text)
    phone = _first_match(r"(?:\+?86[-\s]?)?1[3-9]\d{9}", resume_text)
    city = next(
        (city for city in CITIES if city.casefold() in resume_text.casefold()), ""
    )
    skills = [
        skill
        for skill in SKILL_TERMS
        if re.search(
            rf"(?<![\w.]){re.escape(skill)}(?![\w.])",
            resume_text,
            re.IGNORECASE,
        )
    ]
    # Prefer a short first line that is not contact information as the display name.
    name = next(
        (
            line
            for line in lines[:5]
            if "@" not in line and not re.search(r"\d{6,}", line) and len(line) <= 40
        ),
        "",
    )

    school_line = next(
        (
            line
            for line in lines
            if re.search(r"大学|学院|University|College", line, re.IGNORECASE)
        ),
        "",
    )
    education: list[Education] = []
    if school_line:
        degree = _first_match(
            r"博士|硕士|本科|大专|Ph\.?D\.?|Master|Bachelor", school_line
        )
        graduation_time = _first_match(r"(?:19|20)\d{2}(?:[./-]\d{1,2})?", school_line)
        education.append(
            Education(
                school=school_line,
                major="",
                degree=degree,
                graduation_time=graduation_time,
            )
        )

    project_line = next(
        (line for line in lines if re.search(r"项目|project", line, re.IGNORECASE)),
        "",
    )
    projects: list[ProjectExperience] = []
    if project_line:
        project_name = re.split(r"[:：]", project_line, maxsplit=1)[0].strip()
        projects.append(
            ProjectExperience(
                name=project_name,
                role="",
                start_time="",
                end_time="",
                description=project_line,
                responsibilities=[],
                achievements=[],
                technologies=[
                    skill
                    for skill in skills
                    if skill.casefold() in project_line.casefold()
                ],
            )
        )

    professional_summary = (
        f"简历中明确提及的技能包括：{'、'.join(skills[:8])}。" if skills else ""
    )
    return ResumeData(
        name=name,
        phone=phone,
        email=email,
        city=city,
        professional_summary=professional_summary,
        personal_advantages=[],
        current_title="",
        years_of_experience="",
        job_intention="",
        education=education,
        work_experience=[],
        project_experience=projects,
        skills=skills,
        certifications=[],
        languages=[],
    )


def mock_score(resume_text: str, jd_text: str) -> ScoreResult:
    resume = mock_extract(resume_text)
    jd_skills = [
        skill for skill in SKILL_TERMS if skill.casefold() in jd_text.casefold()
    ]
    resume_skills = {skill.casefold() for skill in resume.skills}
    matched = [skill for skill in jd_skills if skill.casefold() in resume_skills]

    skill_score = round(100 * len(matched) / len(jd_skills)) if jd_skills else 60
    experience_score = (
        75
        if re.search(r"项目|工作经历|experience|project", resume_text, re.IGNORECASE)
        else 50
    )
    education_score = 75 if resume.education else 50
    overall_score = round(
        skill_score * 0.5 + experience_score * 0.35 + education_score * 0.15
    )

    missing = [skill for skill in jd_skills if skill.casefold() not in resume_skills]
    match_summary = "、".join(matched[:5]) or "未识别出明确重合技能"
    missing_summary = "、".join(missing[:5]) or "无明显缺口"
    return ScoreResult(
        overall_score=overall_score,
        skill_score=skill_score,
        experience_score=experience_score,
        education_score=education_score,
        comment=f"Mock 规则评分：匹配技能为 {match_summary}；待核实技能为 {missing_summary}。",
        interview_questions=[
            "请介绍一个最能体现岗位相关能力的项目，以及你承担的具体工作。",
            f"请说明你对 {missing[0] if missing else '岗位核心技术'} 的实际使用经验。",
        ],
    )
