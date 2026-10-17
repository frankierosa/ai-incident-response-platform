class AIServiceError(Exception):
    """Raised when the AI service cannot complete an analysis."""

    def __init__(
        self,
        message: str = "AI analysis is temporarily unavailable.",
    ) -> None:
        self.message = message
        super().__init__(self.message)