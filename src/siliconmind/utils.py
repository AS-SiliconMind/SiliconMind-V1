import re


class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


SYS_PROMPT_INTERNAL_WORKFLOW = "Provided below is a Verilog coding problem, I would like you to:\n\n1. Try solving the Verilog coding problem.\n2. Check whether your attempted solution is syntactically correct and satisfies the problem's requirements. Do this by deriving a couple representative test scenarios and pondering your Verilog design's behavior in each test scenario.\n3. If you find your attempted solution to by faulty, fix it according to your own analysis.\n\nThink first INTERNALLY on step 1 to step 3. Then, output ONLY THE CORRECT Verilog code in this format: <answer>\n```verilog\n...\n```\n</answer>. No explanations, comments, or additional text are allowed outside of the specified formatting."
SYS_PROMPT_ANSWER_GUIDE = "Please solve the following Verilog coding problem. Think first INTERNALLY about how to arrive at the correct solution. Then, output ONLY the Verilog code you designed in this format: <answer>\n```verilog\n...\n```\n</answer>. No explanations, comments, or additional text are allowed outside of the specified formatting."
SYS_PROMPT_QUANT_DUCK_PT1 = "Please check whether the following Verilog design is syntactically correct and satisfies the problem's requirements.\nFirst, derive a couple representative test scenarios.\nThen, ponder the Verilog design's behavior in each test scenario.\nLastly, if you find the Verilog design to be faulty, write [DESIGN NEEDS FIXING] in your output. Otherwise, output [DESIGN IS CORRECT]."
SYS_PROMPT_QUANT_DUCK_PT2 = "Fix the attempted solution to the Verilog design problem using the provided error analysis.\nThink first INTERNALLY about how to arrive at the correct solution. Then, output ONLY the Verilog code you designed in this format: <answer>\n```verilog\n...\n```\n</answer>. No explanations, comments, or additional text are allowed outside of the specified formatting."


def parse_text(text: str) -> str:
    patterns = [r".*?</think>\n*<answer>(.*?)</answer>\n*"]
    matches = [re.fullmatch(pat, text, re.DOTALL) for pat in patterns]
    for match in matches:
        if match:
            return match.group(1).strip()
    return ""


def parse_code(text: str) -> str:
    patterns = [
        r".*?</think>\n*<answer>\n*```verilog(.*?)```\n*</answer>\n*",
        r".*?</think>\n*```verilog(.*?)```\n*",
    ]
    matches = [re.fullmatch(pat, text, re.DOTALL) for pat in patterns]
    for match in matches:
        if match:
            return match.group(1).strip()
    return ""


def parse_text(text: str) -> str:
    patterns = [r".*?</think>\n*<answer>(.*?)</answer>\n*"]
    matches = [re.fullmatch(pat, text, re.DOTALL) for pat in patterns]
    for match in matches:
        if match:
            return match.group(1).strip()
    return ""


def parse_code(text: str) -> str:
    patterns = [
        r".*?</think>\n*<answer>\n*```verilog(.*?)```\n*</answer>\n*",
        r".*?</think>\n*```verilog(.*?)```\n*",
    ]
    matches = [re.fullmatch(pat, text, re.DOTALL) for pat in patterns]
    for match in matches:
        if match:
            return match.group(1).strip()
    return ""


def wrap_text(text: str) -> str:
    return '"""\n' + text + '\n"""'


def wrap_prompt(prompt: str):
    return [{"role": "user", "content": prompt}]


def wrap_code(code: str) -> str:
    return f"```verilog\n{code}\n```"


def get_attempt_prompts(problems: list[str], internal_workflow: bool) -> list:
    pref = (
        SYS_PROMPT_INTERNAL_WORKFLOW if internal_workflow else SYS_PROMPT_ANSWER_GUIDE
    )
    prompts = []
    for prob in problems:
        prompts.append(
            wrap_prompt(pref + "\n\n### Verilog Coding Problem\n\n" + wrap_text(prob))
        )
    return prompts


def get_duck_prompts(problems: list[str], attempts: list[str]) -> list:
    assert len(problems) == len(attempts)

    prompts = []
    for p, a in zip(problems, attempts):
        prompts.append(
            wrap_prompt(
                SYS_PROMPT_QUANT_DUCK_PT1
                + f"\n\n### Problem\n\n{wrap_text(p)}"
                + f"\n\n### Verilog Design\n\n{wrap_code(a)}"
            )
        )
    return prompts


def get_debug_prompts(
    problems: list[str],
    attempts: list[str],
    error_analysis: list[str],
) -> list:
    assert len(problems) == len(attempts) and len(problems) == len(error_analysis)

    prompts = []
    for p, a, e in zip(problems, attempts, error_analysis):
        prompts.append(
            wrap_prompt(
                SYS_PROMPT_QUANT_DUCK_PT2
                + f"\n\n### Verilog Design Problem\n\n{wrap_text(p)}"
                + f"\n\n### Attempted Solution\n\n{wrap_code(a)}"
                + f"\n\n### Error Analysis\n\n{wrap_text(e)}"
            )
        )
    return prompts
