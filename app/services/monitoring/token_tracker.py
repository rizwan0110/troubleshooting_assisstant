import logging
from dataclasses import dataclass, field
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    query: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str


@dataclass
class TokenTracker:
    history: List[TokenUsage] = field(default_factory=list)
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_requests: int = 0

    def track(
        self,
        query: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        model: str,
    ):
        usage = TokenUsage(
            query=query[:100],  # truncate to keep logs readable
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model,
        )
        self.history.append(usage)
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_tokens += total_tokens
        self.total_requests += 1

        logger.info(
            f"Token usage | prompt: {prompt_tokens} | completion: {completion_tokens} | "
            f"total: {total_tokens} | cumulative: {self.total_tokens}"
        )

    def get_summary(self) -> dict:
        avg_tokens = (
            self.total_tokens / self.total_requests if self.total_requests > 0 else 0
        )
        return {
            "total_requests": self.total_requests,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "avg_tokens_per_request": round(avg_tokens, 2),
        }


token_tracker = TokenTracker()
