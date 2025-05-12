from simple_evals.sampler.chat_completion_sampler import ChatCompletionSampler


def test_sampler_basic():
    sampler = ChatCompletionSampler(model="gpt-4o")
    assert callable(sampler.sample)
