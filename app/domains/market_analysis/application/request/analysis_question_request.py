from pydantic import BaseModel


class AnalysisQuestionRequest(BaseModel):
    question: str
