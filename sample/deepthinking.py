import sys
import argparse
from utils import Colors
from vllm import LLM, SamplingParams
from siliconmind.engine import unified_solve

parser = argparse.ArgumentParser(description="Run internal workflow")
parser.add_argument(
    "--model-path",
    type=str,
    required=True,
    help="Path to the LLM model",
)
args = parser.parse_args()
model = LLM(model=args.model_path, max_model_len=16384)
sampling_params = SamplingParams(temperature=1.0, max_tokens=16384)
problem = "I would like you to implement a module named TopModule with the following\ninterface. All input and output ports are one bit unless otherwise\nspecified.\n\n - output zero\n\nThe module should always outputs a LOW.\n\n"

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
