class AIError(Exception):
    """Base error for failures in the AI foundation."""


class AIConfigurationError(AIError):
    """The AI provider is not configured correctly."""


class AIProviderAuthenticationError(AIError):
    """The provider rejected the configured credentials."""


class AIProviderTimeoutError(AIError):
    """The provider request timed out."""


class AIProviderError(AIError):
    """The provider returned or raised an unexpected failure."""


class AIInvalidResponseError(AIError):
    """The provider response could not be parsed or validated."""