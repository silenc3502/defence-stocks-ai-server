from pydantic import BaseModel


class AnalysisAnswerResponse(BaseModel):
    question: str
    answer: str
