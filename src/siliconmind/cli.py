import sys
import argparse
from vllm import LLM, SamplingParams
from siliconmind.engine import solve, debug, unified_solve
from siliconmind.utils import Colors


def run_agentic(model, sampling_params, problem, debug_mode):
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
    if not debug_mode:
        return
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
    return


def run_deepthinking(model, sampling_params, problem):
    code = unified_solve(model, sampling_params, problem)
    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Problem {'='*20}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.CYAN}{problem.strip()}{Colors.END}\n")
    sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*56}{Colors.END}\n")
    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Generated Code {'='*20}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.GREEN}{code.strip()}{Colors.END}\n")
    sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*56}{Colors.END}\n")
    return


def main():
    parser = argparse.ArgumentParser(
        description="SiliconMind: A LLM-based Code Generation Engine for Hardware Design"
    )
    parser.add_argument(
        "--model-path", type=str, required=True, help="Path or repo id to the LLM model"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["deepthinking", "agentic"],
        default="agentic",
        help="Choose the workflow mode",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="I would like you to implement a module named TopModule with the following\ninterface. All input and output ports are one bit unless otherwise\nspecified.\n\n - output zero\n\nThe module should always outputs a LOW.\n\n",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Whether to run in agentic debugging mode"
    )
    args = parser.parse_args()

    model = LLM(model=args.model_path, max_model_len=16384)
    sampling_params = SamplingParams(temperature=1.0, max_tokens=16384)

    if args.mode == "agentic":
        run_agentic(model, sampling_params, args.prompt, args.debug)
    else:
        run_deepthinking(model, sampling_params, args.prompt)

    return


if __name__ == "__main__":
    main()
