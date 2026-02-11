# SiliconMind-V1

This repository contains the codebase of SiliconMind Inference Engine for SiliconMind-V1, a large language model (LLM) fine-tuned for Verilog code generation with multi-agent distillation and debug-reasoning workflows.

- Webpage: https://AS-SiliconMind.github.io/SiliconMind-V1
- Paper: [SiliconMind-V1: Multi-Agent Distillation and Debug-Reasoning Workflows for Verilog Code Generation]()
- Models: [SiliconMind-V1](https://huggingface.co/collections/AS-SiliconMind/siliconmind-v1)

<p align="center">
    <img src="https://github.com/AS-SiliconMind/SiliconMind-V1/blob/gh-pages/images/figure-workflow.webp?raw=true" alt="Framework Overview" width="400">
</p>

## Features

- **RTL Generation**: Generate Verilog code from natural language problem descriptions
- **Multiple Workflows**: *Regular* (default) — single solve pass (agentic without debug) · *Debug* (`--debug`) — iterative solve → trace → debug loop · *Deep Thinking* — single-pass solve + self-debug
- **Reflective Debugging**: Self-review loop: derive test scenarios → evaluate design → fix issues flagged `[DESIGN NEEDS FIXING]`
- **Batch Processing**: Batch variants of all core functions for high-throughput workloads
- **vLLM Integration**: Built on [vLLM](https://github.com/vllm-project/vllm) for high-performance LLM inference
- **CLI**: Ready-to-use command-line entry point (`slcm`)

## Quick Start

> Tested environment: Python 3.12, vLLM 0.15.1

### Installation

```bash
git clone https://github.com/AS-SiliconMind/SiliconMind-V1.git
cd SiliconMind-V1
uv sync  # or `pip install .`
```

### CLI Examples

> Skip `uv run ` if you have run `source .venv/bin/activate` or installed the package globally.
> Streaming mode is used by default for better interactivity. Add `--no-streaming` to disable.

```bash
# Regular (default) — single solve pass
uv run slcm --model-path /path/to/model

# Deep thinking — single-pass solve + self-debug
uv run slcm --model-path /path/to/model --mode deep-thinking

# Agentic — iterative solve → test → debug loop
uv run slcm --model-path /path/to/model --mode agentic

# Custom prompt
uv run slcm --model-path /path/to/model --mode agentic --prompt "I would like you to implement a module named TopModule with the following\ninterface. All input and output ports are one bit unless otherwise\nspecified.\n\n - input  clk\n - input  reset\n - input  data\n - output count (4 bits)\n - output counting\n - output done\n - input  ack\n\nThe module should implement a timer with one input that:\n\n  (1) is started when a particular input pattern (1101) is detected,\n  (2) shifts in 4 more bits to determine the duration to delay,\n  (3) waits for the counters to finish counting, and\n  (4) notifies the user and waits for the user to acknowledge the timer.\n\nThe serial data is available on the data input pin. When the pattern 1101\nis received, the circuit must then shift in the next 4 bits,\nmost-significant-bit first. These 4 bits determine the duration of the\ntimer delay, referred to as delay[3:0]. After that, the state machine\nasserts its counting output to indicate it is counting. Once the 1101 and\ndelay[3:0] have been read, the circuit no longer looks at the data input\nuntil it resumes searching after everything else is done.\n\nThe state machine must count for exactly (delay[3:0] + 1) * 1000 clock\ncycles. e.g., delay=0 means count 1000 cycles, and delay=5 means count\n6000 cycles. Also output the current remaining time. This should be equal\nto delay for 1000 cycles, then delay-1 for 1000 cycles, and so on until\nit is 0 for 1000 cycles.\n\nWhen the circuit isn't counting, the count[3:0] output is don't-care\n(whatever value is convenient for you to implement). At that point, the\ncircuit must assert done to notify the user the timer has timed out, and\nwaits until input ack is 1 before being reset to look for the next\noccurrence of the start sequence (1101).\n\nThe circuit should reset into a state where it begins searching for the\ninput sequence 1101. The reset signal is active high synchronous. Assume\nall sequential logic is triggered on the positive edge of the clock.\n\n"
```

## Python API Examples

### A. Regular Workflow (Default)

Use `solve` for a single-pass generation (regular mode):

```python
from vllm import LLM, SamplingParams
from siliconmind.engine import solve

model = LLM(model="/path/to/model", max_model_len=16384)
params = SamplingParams(temperature=1.0, max_tokens=16384)

problem = (
    "I would like you to implement a module named TopModule with the following\n"
    "interface. All input and output ports are one bit unless otherwise\n"
    "specified.\n\n - output zero\n\n"
    "The module should always outputs a LOW.\n"
)

code = solve(model, params, problem)
```

### B. Deep Thinking Workflow

Use `unified_solve` for a single-pass solve + self-debug:

```python
from vllm import LLM, SamplingParams
from siliconmind.engine import unified_solve

model = LLM(model="/path/to/model", max_model_len=16384)
params = SamplingParams(temperature=1.0, max_tokens=16384)

code = unified_solve(model, params, problem)
```

### C. Agentic Workflow

Use `solve` + `debug` for explicit control over each iteration:

```python
from vllm import LLM, SamplingParams
from siliconmind.engine import solve, debug

model = LLM(model="/path/to/model", max_model_len=16384)
params = SamplingParams(temperature=1.0, max_tokens=16384)

problem = (
    "I would like you to implement a module named TopModule with the following\n"
    "interface. All input and output ports are one bit unless otherwise\n"
    "specified.\n\n - output zero\n\n"
    "The module should always outputs a LOW.\n"
)

code = solve(model, params, problem)

for _ in range(3):
    test, code = debug(model, params, problem, code)
    # test: self-review containing [DESIGN IS CORRECT] or [DESIGN NEEDS FIXING]
    # code: updated only when a fix is applied
```

> Runnable examples: [sample/agentic.py](sample/agentic.py) (regular & debug) · [sample/deepthinking.py](sample/deepthinking.py) · [sample/agentic_batch.py](sample/agentic_batch.py) · [sample/deepthinking_batch.py](sample/deepthinking_batch.py)

## API Reference

### `siliconmind.engine`

#### Single-problem functions

| Function | Returns | Description |
|---|---|---|
| `solve(model, params, problem)` | `str` | Generate Verilog for one problem (agentic workflow) |
| `debug(model, params, problem, attempt)` | `tuple[str, str]` | One round of reflective debugging → `(test, code)` |
| `unified_solve(model, params, problem)` | `str` | Single-pass solve + self-debug (deep thinking workflow) |

#### Batch functions

| Function | Returns | Description |
|---|---|---|
| `solve_batch(model, params, problems)` | `list[str]` | Batch version of `solve` |
| `debug_batch(model, params, problems, attempts)` | `tuple[list[str], list[str]]` | Batch version of `debug` — only `[DESIGN NEEDS FIXING]` entries are re-generated |
| `unified_solve_batch(model, params, problems)` | `list[str]` | Batch version of `unified_solve` |

**Common parameters**

- **model** — an initialized `vllm.LLM` instance
- **params** — a `vllm.SamplingParams` instance
- **problem(s)** — natural-language problem description(s)
- **attempt(s)** — Verilog code to review and potentially fix

## Project Structure

```
SiliconMind-V1/
├── pyproject.toml                    # Package metadata & dependencies
├── sample/
│   ├── agentic.py                   # Agentic workflow example
│   ├── agentic_batch.py             # Agentic batch example
│   ├── deepthinking.py              # Deep thinking workflow example
│   ├── deepthinking_batch.py        # Deep thinking batch example
│   └── utils.py                     # Shared helpers for samples
└── src/siliconmind/
    ├── __init__.py
    ├── cli.py                        # CLI entry point (slcm)
    ├── engine.py                     # Core solve / debug functions
    └── utils.py                      # Prompt construction & output parsing
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Apache License 2.0](LICENSE)
