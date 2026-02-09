import os
import sys
from vllm import LLM, SamplingParams
from siliconmind.engine import unified_solve


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


model_name = "/mnt/llm_team/silicon_mind/qwen3-4b-think_oss-other-duck"
model = LLM(model=model_name, max_model_len=16384)
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
