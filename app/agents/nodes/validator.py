from app.core.config.llm_provider import load_llm
from app.core.config.settings import ALLOWED_CATEGORIES
from app.core.prompt.validator_prompt import validator_prompt
from app.schemas.pydantic_output_schemas.validator_schema import ValidatorSchema

llm = load_llm()
PROMPT = validator_prompt()


def validator_node(state):
    structured_llm = llm.with_structured_output(ValidatorSchema, method='json_mode')
    result: ValidatorSchema = structured_llm.invoke(
        PROMPT.format(
            intent=state["intent"],
            allowed=list(ALLOWED_CATEGORIES)
        )
    )

    state["validated"] = result.validated
    state["missing_info"] = result.missing_info
    return state
