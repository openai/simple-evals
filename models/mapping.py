from models.openai.sampler import GPT4oSampler, GPT4TurboSampler, GPT3_5TurboSampler
from models.anthropic.sampler import Claude3OpusSampler, Claude3SonnetSampler, Claude3HaikuSampler

MODEL_LOADING_MAP = {
    "openai": {
        "gpt-4o": GPT4oSampler,
        "gpt-4-turbo": GPT4TurboSampler,
        "gpt-3.5-turbo": GPT3_5TurboSampler,
    },
    "anthropic": {
        "claude-3-opus": Claude3OpusSampler,
        "claude-3-sonnet": Claude3SonnetSampler,
        "claude-3-haiku": Claude3HaikuSampler,
    }
}

def get_model_server(model_loader: str, model: str):
    return MODEL_LOADING_MAP[model_loader][model]()