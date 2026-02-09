# SiliconMind

A powerful AI agent framework for RTL code generation.

## Features

- **RTL Generation**: Generate Verilog code from natural language problem descriptions.
- **Dual Workflow Modes**:
  - **Internal**: The model solves, self-verifies, and self-corrects in a single generation pass.
  - **External**: A multi-step pipeline where generation and reflective debugging ("duck" debugging) are separate, iterative stages.
- **Reflective Debugging**: An external review loop where the model derives test scenarios, evaluates its own design, and fixes issues flagged as `[DESIGN NEEDS FIXING]`.
- **Batch Processing**: Batch variants of all core functions for high-throughput workloads.
- **VLLM Integration**: Built on VLLM for high-performance LLM inference.
- **CLI Tool**: A ready-to-use command-line entry point (`slcm`).

## Installation

> **Requires Python ≥ 3.12**

### Using `uv` (recommended)

```bash
git clone https://github.com/yourusername/SiliconMind.git
cd SiliconMind
uv pip install .
```

### Using `pip`

```bash
git clone https://github.com/yourusername/SiliconMind.git
cd SiliconMind
pip install .
```

## Usage

### CLI

After installation a `slcm` command is available:

```bash
# Internal workflow (default) — single-pass solve + self-debug
slcm --model-path /path/to/your/model

# External workflow — iterative solve → duck → debug loop
slcm --model-path /path/to/your/model --mode external

# Custom prompt
slcm --model-path /path/to/your/model --prompt "I would like you to implement ..."
```

### Python API — External Workflow

Use `solve` and `debug` when you want explicit control over each iteration:

```python
from vllm import LLM, SamplingParams
from siliconmind.engine import solve, debug

model = LLM(model="/path/to/your/model", max_model_len=16384)
sampling_params = SamplingParams(temperature=1.0, max_tokens=16384)

problem = (
    "I would like you to implement a module named TopModule with the following\n"
    "interface. All input and output ports are one bit unless otherwise\n"
    "specified.\n\n - output zero\n\n"
    "The module should always outputs a LOW.\n"
)

# Step 1 — Generate an initial solution
code = solve(model, sampling_params, problem)

# Step 2 — Iterative reflective debugging
for itr in range(3):
    duck, code = debug(model, sampling_params, problem, code)
    # duck contains the model's self-review (includes [DESIGN IS CORRECT]
    # or [DESIGN NEEDS FIXING]). code is updated only when a fix is applied.
```

### Python API — Internal Workflow

Use `unified_solve` when the model handles solving and self-debugging in one pass:

```python
from vllm import LLM, SamplingParams
from siliconmind.engine import unified_solve

model = LLM(model="/path/to/your/model", max_model_len=16384)
sampling_params = SamplingParams(temperature=1.0, max_tokens=16384)

problem = "..."

code = unified_solve(model, sampling_params, problem)
```

For complete runnable examples, see [sample/external_wf.py](sample/external_wf.py) and [sample/internal_wf.py](sample/internal_wf.py).

## API Reference

### `siliconmind.engine`

#### `solve(model, sampling_params, problem: str) -> str`

Generates Verilog code for a single problem description (external workflow).

- **model**: An initialized `vllm.LLM` instance.
- **sampling_params**: A `vllm.SamplingParams` instance.
- **problem**: The natural-language problem description.
- **Returns**: The generated Verilog code as a string.

#### `debug(model, sampling_params, problem: str, attempt: str) -> tuple[str, str]`

Performs one round of reflective debugging on the given `attempt`. The model first generates a self-review ("duck") that evaluates correctness. If the review contains `[DESIGN NEEDS FIXING]`, a second generation pass produces a corrected design; otherwise the original `attempt` is returned unchanged.

- **problem**: The original problem description.
- **attempt**: The Verilog code to review and potentially fix.
- **Returns**: A tuple `(duck, code)` — the review text and the (possibly updated) code.

#### `unified_solve(model, sampling_params, problem: str) -> str`

Generates Verilog code using the internal workflow, where the model solves, self-verifies, and self-corrects within a single generation pass.

- **Returns**: The generated Verilog code as a string.

#### `solve_batch(model, sampling_params, problems: list[str]) -> list[str]`

Batch version of `solve`.

#### `unified_solve_batch(model, sampling_params, problems: list[str]) -> list[str]`

Batch version of `unified_solve`.

#### `debug_batch(model, sampling_params, problems: list[str], attempts: list[str]) -> list[str]`

Batch version of `debug`. Only designs flagged as `[DESIGN NEEDS FIXING]` are sent through the debug generation pass; the rest are returned as-is.

- **Returns**: The updated list of attempts (in-place mutation and return).

## Project Structure

```
SiliconMind/
├── pyproject.toml                 # Package metadata & dependencies
├── sample/
│   ├── external_wf.py            # External workflow example
│   └── internal_wf.py            # Internal workflow example
└── src/siliconmind/
    ├── __init__.py
    ├── cli.py                     # CLI entry point (slcm)
    ├── engine.py                  # Core solve / debug functions
    └── utils.py                   # Prompt construction & output parsing
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
