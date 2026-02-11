import uuid

from vllm import SamplingParams
from vllm.sampling_params import RequestOutputKind

from siliconmind.utils import (
    get_attempt_prompts,
    get_debug_prompts,
    get_test_prompts,
    parse_code,
    parse_text,
)


def unified_solve(model, sampling_params, problem: str):
    prompt = get_attempt_prompts([problem], internal_workflow=True)[0]
    gen = model.chat([prompt], sampling_params)[0]
    return parse_code(gen.outputs[0].text)


def unified_solve_batch(model, sampling_params, problems: list[str]):
    problems = get_attempt_prompts(problems, internal_workflow=True)
    gens = model.chat(problems, sampling_params)
    outputs = []
    for gen in gens:
        code = parse_code(gen.outputs[0].text)
        outputs.append(code)
    return outputs


def solve(model, sampling_params, problem: str):
    prompt = get_attempt_prompts([problem], internal_workflow=False)[0]
    gen = model.chat([prompt], sampling_params)[0]
    return parse_code(gen.outputs[0].text)


def solve_batch(model, sampling_params, problems: list[str]):
    problems = get_attempt_prompts(problems, internal_workflow=False)
    gens = model.chat(problems, sampling_params)
    outputs = []
    for gen in gens:
        code = parse_code(gen.outputs[0].text)
        outputs.append(code)
    return outputs


def debug(model, sampling_params, problem: str, attempt: str):
    test_prompt = get_test_prompts([problem], [attempt])[0]
    gen = model.chat([test_prompt], sampling_params)[0]
    test = parse_text(gen.outputs[0].text)
    a = "[DESIGN IS CORRECT]" in test
    b = "[DESIGN NEEDS FIXING]" in test
    if (a and b) or (not a and not b):
        return test, attempt
    if a:
        return test, attempt
    debug_prompt = get_debug_prompts([problem], [attempt], [test])[0]
    debug_gen = model.chat([debug_prompt], sampling_params)[0]
    debug_code = parse_code(debug_gen.outputs[0].text)
    if debug_code:
        return test, debug_code
    else:
        return test, attempt


def debug_batch(model, sampling_params, problems, attempts):
    test_prompts = get_test_prompts(problems, attempts)
    gens = model.chat(test_prompts, sampling_params)
    bad_indexes = []
    for i, gen in enumerate(gens):
        test = parse_text(gen.outputs[0].text)
        a = "[DESIGN IS CORRECT]" in test
        b = "[DESIGN NEEDS FIXING]" in test
        if (a and b) or (not a and not b):
            continue
        if b:
            bad_indexes.append((i, test))
    if bad_indexes:
        debug_problems = [problems[i] for i, _ in bad_indexes]
        debug_attempts = [attempts[i] for i, _ in bad_indexes]
        debug_tests = [test for _, test in bad_indexes]
        debug_prompts = get_debug_prompts(debug_problems, debug_attempts, debug_tests)
        debug_gens = model.chat(debug_prompts, sampling_params)
        for i, gen in enumerate(debug_gens):
            debug_code = parse_code(gen.outputs[0].text)
            if debug_code:
                attempts[bad_indexes[i][0]] = debug_code
    return attempts


# ---------------------------------------------------------------------------
# Streaming support (AsyncLLM / V1 engine)
# ---------------------------------------------------------------------------


async def _stream_chat(engine, sampling_params, messages, tokenizer, print_fn=None):
    """Stream a chat completion using AsyncLLM.

    Prints token deltas via *print_fn* as they arrive and returns the full
    accumulated text once generation is finished.
    """
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    stream_params = SamplingParams(
        temperature=sampling_params.temperature,
        max_tokens=sampling_params.max_tokens,
        output_kind=RequestOutputKind.DELTA,
    )

    request_id = str(uuid.uuid4())
    full_text = ""

    async for output in engine.generate(
        request_id=request_id,
        prompt=prompt,
        sampling_params=stream_params,
    ):
        for completion in output.outputs:
            if completion.text:
                full_text += completion.text
                if print_fn:
                    print_fn(completion.text)
        if output.finished:
            break

    return full_text


async def solve_streaming(engine, sampling_params, problem, tokenizer, print_fn=None):
    prompt = get_attempt_prompts([problem], internal_workflow=False)[0]
    full_text = await _stream_chat(engine, sampling_params, prompt, tokenizer, print_fn)
    return parse_code(full_text)


async def unified_solve_streaming(
    engine, sampling_params, problem, tokenizer, print_fn=None
):
    prompt = get_attempt_prompts([problem], internal_workflow=True)[0]
    full_text = await _stream_chat(engine, sampling_params, prompt, tokenizer, print_fn)
    return parse_code(full_text)


async def debug_streaming(
    engine, sampling_params, problem, attempt, tokenizer, print_fn=None
):
    # --- test phase (streamed) ---
    test_prompt = get_test_prompts([problem], [attempt])[0]
    full_text = await _stream_chat(
        engine, sampling_params, test_prompt, tokenizer, print_fn
    )
    test = parse_text(full_text)

    a = "[DESIGN IS CORRECT]" in test
    b = "[DESIGN NEEDS FIXING]" in test
    if (a and b) or (not a and not b):
        return test, attempt
    if a:
        return test, attempt

    # --- debug/fix phase (streamed) ---
    debug_prompt = get_debug_prompts([problem], [attempt], [test])[0]
    debug_text = await _stream_chat(
        engine, sampling_params, debug_prompt, tokenizer, print_fn
    )
    debug_code = parse_code(debug_text)
    if debug_code:
        return test, debug_code
    else:
        return test, attempt
