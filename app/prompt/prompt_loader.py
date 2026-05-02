import yaml
from pathlib import Path

_prompts = None


def load_prompts():
    global _prompts
    if _prompts is None:
        path = Path(__file__).parent / "prompt.yaml"
        with open(path) as f:
            _prompts = yaml.safe_load(f)
    return _prompts


def get_prompt(name: str) -> str:
    prompts = load_prompts()
    return prompts[name]
