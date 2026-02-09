import sys
import argparse
from utils import Colors
from vllm import LLM, SamplingParams
from siliconmind.engine import solve_batch, debug_batch


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

problems = [
    "I would like you to implement a module named TopModule with the following\ninterface. All input and output ports are one bit unless otherwise\nspecified.\n\n - output zero\n\nThe module should always outputs a LOW.\n\n",
    "I would like you to implement a module named TopModule with the following\ninterface. All input and output ports are one bit unless otherwise\nspecified.\n\n - input  in\n - output out\n\nThe module should implement a NOT gate.\n\n",
]

outputs = solve_batch(model, sampling_params, problems)
for i, (problem, code) in enumerate(zip(problems, outputs), 1):
    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Problem {i} {'='*20}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.CYAN}{problem.strip()}{Colors.END}\n")
    sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*56}{Colors.END}\n")
    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Initial Solution {'='*20}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.GREEN}{code.strip()}{Colors.END}\n")
    sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*56}{Colors.END}\n")

for itr in range(1, 4):
    ducks, outputs = debug_batch(model, sampling_params, problems, outputs)
    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Debugging Iteration = {itr} {'='*20}{Colors.END}\n"
    )
    for i, (problem, duck, code) in enumerate(zip(problems, ducks, outputs), 1):
        sys.stdout.write(
            f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Problem {i} {'-'*20}{Colors.END}\n"
        )
        sys.stdout.write(f"{Colors.CYAN}{problem.strip()}{Colors.END}\n")
        sys.stdout.write(
            f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Duck {'-'*20}{Colors.END}\n"
        )
        sys.stdout.write(f"{Colors.GREEN}{duck.strip()}{Colors.END}\n")
        sys.stdout.write(
            f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Debug Code {'-'*20}{Colors.END}\n"
        )
        sys.stdout.write(f"{Colors.GREEN}{code.strip()}{Colors.END}\n")
        sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*56}{Colors.END}\n")
    sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*56}{Colors.END}\n")
