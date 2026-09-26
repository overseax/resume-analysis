from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("*", mode="before")
    @classmethod
    def normalize_null_strings(cls, value: object) -> object:
        return "" if value is None else value


class Education(StrictModel):
    school: str = Field(description="学校名称，未知时为空字符串")
    major: str = Field(description="专业，未知时为空字符串")
    degree: str = Field(description="学历，未知时为空字符串")
    graduation_time: str = Field(description="毕业时间，未知时为空字符串")


class WorkExperience(StrictModel):
    company: str = Field(description="公司或组织名称，未知时为空字符串")
    title: str = Field(description="职位名称，未知时为空字符串")
    location: str = Field(description="工作地点，未知时为空字符串")
    start_time: str = Field(description="开始时间，保持原文格式，未知时为空字符串")
    end_time: str = Field(description="结束时间或至今，保持原文格式，未知时为空字符串")
    responsibilities: list[str] = Field(description="主要职责，只保留原文有依据的信息")
    achievements: list[str] = Field(description="业绩与量化成果，保留原文数字")
    technologies: list[str] = Field(description="该段经历明确使用的技术或工具")


class ProjectExperience(StrictModel):
    name: str = Field(description="项目名称，未知时为空字符串")
    role: str = Field(description="候选人在项目中的角色，未知时为空字符串")
    start_time: str = Field(description="开始时间，保持原文格式，未知时为空字符串")
    end_time: str = Field(description="结束时间或至今，保持原文格式，未知时为空字符串")
    description: str = Field(description="项目背景和目标，未知时为空字符串")
    responsibilities: list[str] = Field(description="候选人承担的工作")
    achievements: list[str] = Field(description="项目成果与量化指标，保留原文数字")
    technologies: list[str] = Field(description="项目明确使用的技术或工具")


class ResumeData(StrictModel):
    name: str = Field(description="候选人姓名，未知时为空字符串")
    phone: str = Field(description="电话号码，未知时为空字符串")
    email: str = Field(description="邮箱，未知时为空字符串")
    city: str = Field(description="所在城市，未知时为空字符串")
    professional_summary: str = Field(
        description="基于简历事实生成的两到四句职业概况，不评价简历缺失项"
    )
    personal_advantages: list[str] = Field(
        description="有简历证据支撑的个人优势，避免空泛形容词"
    )
    current_title: str = Field(
        description="最近一段工作经历中的职位，不得使用项目名称，无法确认时为空字符串"
    )
    years_of_experience: str = Field(
        description="根据明确工作时间计算的经验年限，无法计算时为空字符串"
    )
    job_intention: str = Field(description="简历明确写出的求职意向，未知时为空字符串")
    education: list[Education]
    work_experience: list[WorkExperience]
    project_experience: list[ProjectExperience]
    skills: list[str]
    certifications: list[str] = Field(description="证书、资格或专业认证")
    languages: list[str] = Field(description="语言及简历中明确给出的熟练程度")

    @model_validator(mode="after")
    def remove_unsupported_experience(self) -> "ResumeData":
        self.work_experience = [
            item
            for item in self.work_experience
            if any(
                (
                    item.company,
                    item.title,
                    item.start_time,
                    item.end_time,
                    item.responsibilities,
                    item.achievements,
                )
            )
        ]
        self.project_experience = [
            item
            for item in self.project_experience
            if any(
                (
                    item.name,
                    item.description,
                    item.responsibilities,
                    item.achievements,
                )
            )
        ]
        if not self.work_experience:
            self.current_title = ""
        return self


class ScoreResult(StrictModel):
    overall_score: int = Field(ge=0, le=100)
    skill_score: int = Field(ge=0, le=100)
    experience_score: int = Field(ge=0, le=100)
    education_score: int = Field(ge=0, le=100)
    comment: str = Field(min_length=1)
    interview_questions: list[str] = Field(min_length=1)
