"""Agent for executing kubectl commands."""
from autogen.agentchat import UserProxyAgent

READ_ONLY_COMMANDS = ["get", "describe", "explain", "logs", "top", "events", "api-versions", "cluster-info"]
BLOCKING_COMMANDS = ["edit", "--watch", "-w"]


class KubectlExecutorAgent(UserProxyAgent):
    """An agent for running kubectl commands.

    If running in read only mode (default), it will prevent create, read,
    update or delete commands from being executed.
    """

    def __init__(self, *args, read_only=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_only = read_only

    def execute_code_blocks(self, code_blocks):
        """Execute kubectl command code blocks and returns the result.

        Args:
        ----
        code_blocks (list): kubectl commands to execute.

        Returns:
        -------
        A tuple of (exitcode, logs_all).
            exitcode (int): 0 if the code execution was successful, else non-zero.
            logs_all (str): The output of the code execution.
        """
        exitcode = 0
        logs_all = ""

        for code_block in code_blocks:
            lang, code = code_block

            if lang not in ("bash", "sh", "shell"):
                continue

            code = code.strip()

            if not code.startswith("kubectl"):
                return 1, f"'{code}' is not a kubectl command."

            if any(command in code for command in (BLOCKING_COMMANDS)):
                return (
                    1,
                    f"You cannot use the following commands/options, {BLOCKING_COMMANDS}, as they block execution.",
                )

            if self.read_only:
                if not any(command in code.split()[:2] for command in (READ_ONLY_COMMANDS)):
                    return (
                        1,
                        (f"\n'{code}' is not a read only operation. " "You can only perform read only operations.\n"),
                    )

            exitcode, logs, image = self.run_code(code, lang="bash", **self._code_execution_config)

            if image is not None:
                self._code_execution_config["use_docker"] = image
            logs_all += "\n" + logs
            if exitcode != 0:
                return exitcode, logs_all

        return exitcode, logs_all
