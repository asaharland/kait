"""Entry point for CLI."""
import os
from datetime import datetime
import click
from kait.kubernetes_debugger import KubernetesDebugger


@click.group()
def cli():
    """CLI wrapper."""


@cli.command()
@click.argument("request")
@click.option(
    "--read-only",
    default=True,
    help="Flag for whether the command runs in read only mode or not. Defaults to true.",
)
@click.option(
    "--input-mode",
    type=click.Choice(["ALWAYS", "NEVER", "TERMINATE"], case_sensitive=False),
    default="NEVER",
    help="""
Defines whether kait should wait for human input or not (defaults to NEVER).
NEVER: Never prompt for user input;
ALWAYS: User will be requested for feedback after each step;
TERMINATE: User will be requested for feedback at the end of the debugging session.
""",
)
@click.option("--max-replies", type=int, default=10, help="Maximum number of replies before a session terminates.")
@click.option("--output-dir", help="Output directory to store the debug output markdown file.")
def debug(request, read_only, input_mode, max_replies, output_dir):
    """Debugs and fixes issues with kubernetes resources based on the provided REQUEST."""
    if os.getenv("KAIT_OPENAI_KEY") is None:
        print(
            """
The environment variable 'KAIT_OPENAI_KEY' is not set.

Set the environment variable 'KAIT_OPENAI_KEY' with your OpenAI config e.g.:
[
    {
        "model": "gpt-4",
        "api_key": "YOUR_OPENAI_API_KEY"
    }
]
"""
        )
        return

    output_file: str = None
    if output_dir:
        file_date_key = datetime.today().strftime("%Y%m%d%H%M%S")
        output_file = f"{output_dir}/kait_debug_{file_date_key}.md"

        with open(output_file, encoding="UTF-8", mode="a") as file:
            file.write("## Request\n")
            file.write(f"{request}\n\n")
            file.write("## Response\n")

    debugger = KubernetesDebugger(
        read_only=read_only,
        output_file=output_file,
        input_mode=input_mode,
        max_replies=max_replies,
    )
    debugger.debug(request=request)


if __name__ == "__main__":
    cli()
