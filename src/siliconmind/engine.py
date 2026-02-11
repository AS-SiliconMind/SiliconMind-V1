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
