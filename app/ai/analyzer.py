import os

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# NOTE: Instead of trusting the LLM to return correctly formatted JSON, we're asking it to produce structured data that matches our Pydantic model.
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
        description="Recommended actions for investigating or resolving the incident."
    )



def create_ai_analyzer():
    """Create the LLM configured for incident analysis."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )

    return llm.with_structured_output(IncidentAnalysis)



def analyze_incident(incident: dict) -> IncidentAnalysis:
    """Analyze an incident using the configured LLM."""

    analyzer = create_ai_analyzer()

    prompt = f"""
You are a production incident response assistant.

Analyze the following production incident.

Incident:
{incident}

Provide:
1. A concise summary.
2. The most probable cause based only on the available information.
3. The likely impact.
4. Recommended investigation or remediation actions.

Do not claim certainty when the available information is insufficient.
Clearly distinguish probable causes from confirmed facts.
"""

    return analyzer.invoke(prompt)