import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


# Load the project's .env file explicitly
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)

# Define the structured output model for incident analysis
class IncidentAnalysis(BaseModel):
    """Structured AI analysis of a production incident."""

    summary: str = Field(
        description="A concise summary of the incident."
    )

    probable_cause: str = Field(
        description="The most likely cause based on the incident information."
    )

    impact: str = Field(
        description="The likely impact of the incident on users or systems."
    )

    recommended_actions: list[str] = Field(
        description=(
            "Recommended actions for investigating or resolving "
            "the incident."
        )
    )


def create_ai_analyzer():
    """Create the LLM configured for incident analysis."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key,
    )

    return llm.with_structured_output(IncidentAnalysis)


def analyze_incident(
    incident: dict,
    knowledge_context: list[str] | None = None,
) -> IncidentAnalysis:
    """Analyze an incident using the configured LLM and runbook knowledge."""

    analyzer = create_ai_analyzer()

    if knowledge_context:
        knowledge_text = "\n\n".join(
            f"Knowledge Chunk {index + 1}:\n{chunk}"
            for index, chunk in enumerate(knowledge_context)
        )
    else:
        knowledge_text = "No relevant runbook knowledge was found."

    prompt = f"""
You are a production incident response assistant.

Analyze the following production incident.

Incident:
{incident}

Relevant operational knowledge from internal runbooks:
{knowledge_text}

Use the provided runbook knowledge when it is relevant.

Provide:
1. A concise summary.
2. The most probable cause based only on the available information.
3. The likely impact.
4. Recommended investigation or remediation actions.

Do not claim certainty when the available information is insufficient.
Clearly distinguish probable causes from confirmed facts.
Do not invent information that is not present in the incident or
provided runbook knowledge.
"""

    result = analyzer.invoke(prompt)

    return IncidentAnalysis.model_validate(result)