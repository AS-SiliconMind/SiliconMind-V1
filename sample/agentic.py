import argparse
import sys
from vllm import LLM, SamplingParams
from siliconmind.engine import solve, debug

from llm_serving.vllm.vllm_repo.tests.models.language.pooling.test_scoring import (
    model_name,
)


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


paser = argparse.ArgumentParser(description="Run external workflow")
paser.add_argument(
    "--model-path",
    type=str,
    required=True,
    help="Path to the LLM model",
)
args = paser.parse_args()
model = LLM(model=args.model_path, max_model_len=16384)
sampling_params = SamplingParams(temperature=1.0, max_tokens=16384)
problem = "I would like you to implement a module named TopModule with the following\ninterface. All input and output ports are one bit unless otherwise\nspecified.\n\n - output zero\n\nThe module should always outputs a LOW.\n\n"

sys.stdout.write(
    f"\n{Colors.HEADER}{Colors.BOLD}{'='*26} Problem {'='*26}{Colors.END}\n"
)
sys.stdout.write(f"{Colors.CYAN}{problem.strip()}{Colors.END}\n")
sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*64}{Colors.END}\n")

code = solve(model, sampling_params, problem)

sys.stdout.write(
    f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Generated Code {'='*20}{Colors.END}\n"
)
sys.stdout.write(f"{Colors.GREEN}{code.strip()}{Colors.END}\n")
sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*64}{Colors.END}\n")

for itr in range(1, 4):
    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Debugging Iteration = {itr} {'='*20}{Colors.END}\n"
    )
    duck, code = debug(model, sampling_params, problem, code)
    sys.stdout.write(
        f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Duck {'-'*20}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.GREEN}{duck.strip()}{Colors.END}\n")
    sys.stdout.write(
        f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Debug Code {'-'*20}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.GREEN}{code.strip()}{Colors.END}\n")
    sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*64}{Colors.END}\n")
