![Python Version](https://img.shields.io/badge/3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)

# Kait (Kubernetes AI Tool)

`kait` is an AI assisted kubernetes debugging tool which automatically troubleshoots, diagnoses, and fixes issues related to kubernetes.

`kait` uses autonomous AI agents built using Microsoft's [AutoGen](https://microsoft.github.io/autogen/)

## Installation and setup

You can install `kait` directly using pip:

```bash
pip install kait
```

`kait` requires an OpenAI API key which is read via the environment variable KAIT_OPENAI_KEY. You can provide a list of models to use and `kait` will use the available model. It is recommended to use models with the capabilities of gpt-4. Larger contexts work better too e.g. 'gpt-4-1106-preview'. Your environment variable needs to point to a list of models in the following format:

```
[
    {
        "model": "gpt-4",
        "api_key": "YOUR_OPENAI_API_KEY"
    }
]
```

### Using a Local LLM

You can use OpenAI compatible local LLMs by including a `base_url` in your model spec:

```
[
    {
        "model": "chatglm2-6b",
        "base_url": "http://localhost:8000/v1",
        "api_key": "NULL", # Any string will do
    }
]
```

[FastChat/](https://github.com/lm-sys/FastChat) and [llama-cpp-python](https://llama-cpp-python.readthedocs.io/en/latest/) both provide OpenAI compatible APIs which can be used with the above config. Which models provide adequate performance still needs validating.

## Usage

`kait` requires kubectl to be installed and authenticated against the cluster you want to use.

To run `kait` simply run:

```bash
kait debug <DESCRIPTION OF THE ISSUE TO DEBUG>
```

For a full list of options, run:

```bash
kait debug --help
```

## Examples

A number of [examples/](examples/README.md) are provided so you can see how `kait` performs.
