import argparse
import sys

from llm_serving.vllm.vllm_repo.tests.tool_use.test_deepseekv31_tool_parser import (
    parser,
)
from utils import Colors
from vllm import LLM, SamplingParams

from siliconmind.engine import debug, solve

paser = argparse.ArgumentParser(description="Run external workflow")
paser.add_argument(
    "--model-path",
    type=str,
    required=True,
    help="Path to the LLM model",
)
parser.add_argument(
    "--debug", action="store_true", help="Whether to run in agentic debugging mode"
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

if args.debug:
    for itr in range(1, 4):
        sys.stdout.write(
            f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Debugging Iteration = {itr} {'='*20}{Colors.END}\n"
        )
        test, code = debug(model, sampling_params, problem, code)
        sys.stdout.write(
            f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Test {'-'*20}{Colors.END}\n"
        )
        sys.stdout.write(f"{Colors.GREEN}{test.strip()}{Colors.END}\n")
        sys.stdout.write(
            f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Debug Code {'-'*20}{Colors.END}\n"
        )
        sys.stdout.write(f"{Colors.GREEN}{code.strip()}{Colors.END}\n")
        sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*64}{Colors.END}\n")
