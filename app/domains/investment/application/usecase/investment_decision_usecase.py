from app.domains.investment.adapter.outbound.agent.graph import (
    run_investment_workflow,
)
from app.domains.investment.application.response.investment_decision_response import (
    InvestmentDecisionResponse,
)


class InvestmentDecisionUseCase:
    def execute(self, query: str) -> InvestmentDecisionResponse:
        result = run_investment_workflow(query)
        return InvestmentDecisionResponse(
            answer=result.get("final_output") or "응답을 생성하지 못했습니다.",
        )
