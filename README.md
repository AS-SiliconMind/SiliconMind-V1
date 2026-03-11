<p align="center">
    <img src="https://github.com/AS-SiliconMind/SiliconMind-V1/blob/gh-pages/images/logo.webp?raw=true" alt="SiliconMind Logo" width="400">
</p>

<h1><p align="center">
SiliconMind-V1: Multi-Agent Distillation and Debug-Reasoning Workflows for Verilog Code Generation
</p></h1>

<div align="center">
    <a href="https://drive.google.com/file/d/1-Ismn1EVEYBG1bxFYlE5NvOjakEk6RuC/view?usp=drive_link" target="_blank"><img alt="whitepaper" src="https://img.shields.io/badge/whitepaper-SiliconMind--V1-blue.svg?style=flat" /></a>
    <a href="https://arxiv.org/abs/2603.08719" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2603.08719-b31b1b.svg?style=flat" /></a>
    <a href="https://huggingface.co/collections/AS-SiliconMind/siliconmind-v1" target="_blank"><img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-SiliconMind--V1-ffc107?color=ffc107&logoColor=white" /></a>
</div>

SiliconMind-V1 is a family of open-source Large Language Models (LLMs) specialized for Verilog code generation, testing, and debugging. Unlike previous approaches that rely heavily on commercial models or external EDA tools, SiliconMind-V1 is locally fine-tuned to iteratively generate, test, and debug RTL designs through test-time scaling.

This repository contains the codebase of SiliconMind Inference Engine for SiliconMind-V1, a large language model (LLM) fine-tuned for Verilog code generation with multi-agent distillation and debug-reasoning workflows.

- Webpage: https://AS-SiliconMind.github.io/SiliconMind-V1

<p align="center">
    <img src="https://github.com/AS-SiliconMind/SiliconMind-V1/blob/gh-pages/images/figure-workflow.webp?raw=true" alt="SiliconMind Inference Engine" width="400">
</p>

## Features

- **RTL Generation**: Generate Verilog code from natural language problem descriptions
- **Multiple Workflows**: *Regular* (default) — single solve pass (agentic without debug) · *Deep Thinking* — single-pass solve + self-debug · *Agentic* — iterative solve → trace → debug loop
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
```

```bash
# Custom prompt
uv run slcm --model-path /path/to/model --mode agentic --prompt "I would like you to implement a module named TopModule with the following\ninterface. All input and output ports are one bit unless otherwise\nspecified.\n\n - input  clk\n - input  resetn\n - input  r (3 bits)\n - output g (3 bits)\n\nThe module should implement the FSM described by the state diagram shown\nbelow:\n\n  A        --r0=0,r1=0,r2=0--> A\n  A        -------r0=1-------> B\n  A        -----r0=0,r1=1----> C\n  A        --r0=0,r1=0,r2=0--> D\n  B (g0=1) -------r0=1-------> B\n  B (g0=1) -------r0=0-------> A\n  C (g1=1) -------r1=1-------> C\n  C (g1=1) -------r1=0-------> A\n\nResetn is an active-low synchronous reset that resets into state A. This\nFSM acts as an arbiter circuit, which controls access to some type of\nresource by three requesting devices. Each device makes its request for\nthe resource by setting a signal _r[i]_ = 1, where _r[i]_ is either\n_r[0]_, _r[1]_, or _r[2]_. Each r[i] is an input signal to the FSM, and\nrepresents one of the three devices. The FSM stays in state _A_ as long\nas there are no requests. When one or more request occurs, then the FSM\ndecides which device receives a grant to use the resource and changes to\na state that sets that device's _g[i]_ signal to 1. Each _g[i]_ is an\noutput from the FSM. There is a priority system, in that device 0 has a\nhigher priority than device 1, and device 2 has the lowest priority.\nHence, for example, device 2 will only receive a grant if it is the only\ndevice making a request when the FSM is in state _A_. Once a device, _i_,\nis given a grant by the FSM, that device continues to receive the grant\nas long as its request, _r[i]_ = 1.\n\nImplement a module that represents this FSM. Use separate always blocks\nfor the state table and the state flip-flops, as done in lectures.\nDescribe the FSM outputs, _g[i]_, using either continuous assignment\nstatement(s) or an always block (at your discretion). Assign any state\ncodes that you wish to use. Assume all sequential logic is triggered on\nthe positive edge of the clock.\n\n"
```

> See our [demo video](https://youtu.be/FNclOkRrrsw) for the custom prompt example in action.

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
