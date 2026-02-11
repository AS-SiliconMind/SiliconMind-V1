import argparse
import asyncio
import sys

from vllm import LLM, SamplingParams

from siliconmind.engine import (
    debug,
    debug_streaming,
    solve,
    solve_streaming,
    unified_solve,
    unified_solve_streaming,
)
from siliconmind.utils import Colors


def _print_stream(text):
    """Print streaming text immediately without buffering."""
    sys.stdout.write(text)
    sys.stdout.flush()


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


# ---------------------------------------------------------------------------
# Streaming variants (AsyncLLM / V1 engine)
# ---------------------------------------------------------------------------


async def run_agentic_streaming(
    engine, sampling_params, problem, debug_mode, tokenizer
):
    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*26} Problem {'='*26}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.CYAN}{problem.strip()}{Colors.END}\n")

    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Streaming Response {'='*20}{Colors.END}\n"
    )
    sys.stdout.write(Colors.GREEN)
    code = await solve_streaming(
        engine, sampling_params, problem, tokenizer, _print_stream
    )
    sys.stdout.write(Colors.END + "\n")

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
        sys.stdout.write(Colors.GREEN)
        test, code = await debug_streaming(
            engine, sampling_params, problem, code, tokenizer, _print_stream
        )
        sys.stdout.write(Colors.END + "\n")

        sys.stdout.write(
            f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Test {'-'*20}{Colors.END}\n"
        )
        sys.stdout.write(f"{Colors.GREEN}{test.strip()}{Colors.END}\n")
        sys.stdout.write(
            f"\n{Colors.WARNING}{Colors.BOLD}{'-'*20} Debug Code {'-'*20}{Colors.END}\n"
        )
        sys.stdout.write(f"{Colors.GREEN}{code.strip()}{Colors.END}\n")
        sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*64}{Colors.END}\n")


async def run_deepthinking_streaming(engine, sampling_params, problem, tokenizer):
    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Problem {'='*20}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.CYAN}{problem.strip()}{Colors.END}\n")

    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Streaming Response {'='*20}{Colors.END}\n"
    )
    sys.stdout.write(Colors.GREEN)
    code = await unified_solve_streaming(
        engine, sampling_params, problem, tokenizer, _print_stream
    )
    sys.stdout.write(Colors.END + "\n")

    sys.stdout.write(
        f"\n{Colors.HEADER}{Colors.BOLD}{'='*20} Generated Code {'='*20}{Colors.END}\n"
    )
    sys.stdout.write(f"{Colors.GREEN}{code.strip()}{Colors.END}\n")
    sys.stdout.write(f"\n{Colors.HEADER}{Colors.BOLD}{'='*56}{Colors.END}\n")


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
        choices=["regular", "deep-thinking", "agentic"],
        default="regular",
        help="Choose the workflow mode",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="I would like you to implement a module named TopModule with the following\ninterface. All input and output ports are one bit unless otherwise\nspecified.\n\n - output zero\n\nThe module should always outputs a LOW.\n\n",
    )
    parser.add_argument(
        "--no-streaming",
        action="store_true",
        default=False,
        help="Disable streaming mode (wait for full response before printing)",
    )
    args = parser.parse_args()

    sampling_params = SamplingParams(temperature=1.0, max_tokens=16384)

    if args.no_streaming:
        # Original non-streaming mode
        model = LLM(model=args.model_path, max_model_len=16384)
        if args.mode == "regular":
            run_agentic(model, sampling_params, args.prompt, debug_mode=False)
        elif args.mode == "agentic":
            run_agentic(model, sampling_params, args.prompt, debug_mode=True)
        else:  # deep-thinking
            run_deepthinking(model, sampling_params, args.prompt)
    else:
        # Streaming mode (default)
        asyncio.run(_main_streaming(args, sampling_params))

    return


async def _main_streaming(args, sampling_params):
    from transformers import AutoTokenizer
    from vllm.engine.arg_utils import AsyncEngineArgs
    from vllm.v1.engine.async_llm import AsyncLLM

    engine_args = AsyncEngineArgs(model=args.model_path, max_model_len=16384)
    engine = AsyncLLM.from_engine_args(engine_args)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path)

    try:
        if args.mode == "regular":
            await run_agentic_streaming(
                engine, sampling_params, args.prompt, False, tokenizer
            )
        elif args.mode == "agentic":
            await run_agentic_streaming(
                engine, sampling_params, args.prompt, True, tokenizer
            )
        else:  # deep-thinking
            await run_deepthinking_streaming(
                engine, sampling_params, args.prompt, tokenizer
            )
    finally:
        engine.shutdown()


if __name__ == "__main__":
    main()
