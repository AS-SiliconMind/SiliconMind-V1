from siliconmind.utils import (
    get_attempt_prompts,
    parse_code,
    get_duck_prompts,
    get_debug_prompts,
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
    duck_prompt = get_duck_prompts([problem], [attempt])[0]
    gen = model.chat([duck_prompt], sampling_params)[0]
    duck = parse_text(gen.outputs[0].text)
    a = "[DESIGN IS CORRECT]" in duck
    b = "[DESIGN NEEDS FIXING]" in duck
    if (a and b) or (not a and not b):
        return duck, attempt
    if a:
        return duck, attempt
    debug_prompt = get_debug_prompts([problem], [attempt], [duck])[0]
    debug_gen = model.chat([debug_prompt], sampling_params)[0]
    debug_code = parse_code(debug_gen.outputs[0].text)
    if debug_code:
        return duck, debug_code
    else:
        return duck, attempt


def debug_batch(model, sampling_params, problems, attempts):
    duck_prompts = get_duck_prompts(problems, attempts)
    gens = model.chat(duck_prompts, sampling_params)
    bad_indexes = []
    for i, gen in enumerate(gens):
        duck = parse_text(gen.outputs[0].text)
        a = "[DESIGN IS CORRECT]" in duck
        b = "[DESIGN NEEDS FIXING]" in duck
        if (a and b) or (not a and not b):
            continue
        if b:
            bad_indexes.append((i, duck))
    if bad_indexes:
        debug_problems = [problems[i] for i, _ in bad_indexes]
        debug_attempts = [attempts[i] for i, _ in bad_indexes]
        debug_ducks = [duck for _, duck in bad_indexes]
        debug_prompts = get_debug_prompts(debug_problems, debug_attempts, debug_ducks)
        debug_gens = model.chat(debug_prompts, sampling_params)
        for i, gen in enumerate(debug_gens):
            debug_code = parse_code(gen.outputs[0].text)
            if debug_code:
                attempts[bad_indexes[i][0]] = debug_code
    return attempts
