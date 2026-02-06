from siliconmind.utils import get_attempt_prompts, parse_code


def unified_solve(model, sampling_params, problems: list[str]):
    problems = get_attempt_prompts(problems, internal_workflow=True)
    gens = model.chat(problems, sampling_params)
    outputs = []
    for gen in gens:
        output = []
        for output in gen.outputs:
            code = parse_code(output.text)
            output.append(code)
        outputs.append(output)
    return outputs
