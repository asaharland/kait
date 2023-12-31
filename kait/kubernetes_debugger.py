"""Agent framework for debugging kubernetes."""
import autogen
from colorama import Fore, Style

from kait.kubectl_executor_agent import KubectlExecutorAgent


class KubernetesDebugger:
    """Kubernetes debugger agent framework.

    The kubernetes debugging framework consisting of:
    - A kubernetes admin agent who performs the debugging
    - A code executor agent who runs the code suggested by the kubernetes admin

    These agents work together to solve the problem outlined by the user.
    """

    def __init__(self, read_only, output_file, input_mode: str = "NEVER", max_replies: int = 10):
        self.read_only = read_only
        self.output_file = output_file
        self.input_mode = input_mode
        self.max_replies = max_replies

        self.config_list = autogen.config_list_from_json(
            env_or_file="KAIT_OPENAI_KEY",
        )

        self.kubernetes_agent = self._setup_kubernetes_admin_agent()
        self.code_agent = self._setup_code_executor_agent()

    def _setup_kubernetes_admin_agent(self):
        if self.read_only:
            read_only_clause = """
You only have read only permissions to the cluster. You cannot create, update or delete
resources on the cluster, but you can use the following commands; 'get', 'describe', 'logs', 'top', 'events'.
You can propose changes for the end user to run to fix the command afterwards.
"""
        else:
            read_only_clause = ""

        kubernetes_agent = autogen.AssistantAgent(
            name="kait",
            system_message=f"""
# Your Role
You are an expert Kubernetes administrator and your job is to resolve issues relating to
Kubernetes deployments using kubectl. Do not try and debug the issue with the containers themselves
and only focus on issues relating to kubernetes itself. You are already logged in to the cluster.

# How to present code
You must only provide one command to execute at a time. Never put placeholders like <pod-name> or
<service-name> in your code. Make sure you limit the output when running 'kubectl logs' using the
--tail or --since flags; if using --tail limit logs to the last 10 records.
Do not use the 'kubectl edit' command.

{read_only_clause}

# Useful kubectl command
get: Get resources deployed to the cluster.
describe: Provides details about resources deployed on the cluster.
logs: Get Pod logs.
top: Show CPU and memory metrics.
events: Lists all warning events.
apply: Declaratively create resources on the cluster.
create: Imperatively create resources on the cluster.
patch: Partially update a resource
expose: Create a service

# How to terminate the debug session
Don't ask if the user needs any further assistance, simply reply with 'TERMINATE' if you
have completed the task to the best of your abilities. If you need the user to save code to a file
or you have no code left to run, respond with 'TERMINATE'.
""",
            llm_config={
                "timeout": 600,
                "cache_seed": 42,
                "config_list": self.config_list,
                "temperature": 0,
            },
            code_execution_config={
                "use_docker": False,
            },
        )

        def output_message(recipient, messages, sender, config):
            if "callback" in config and config["callback"] is not None:
                callback = config["callback"]
                callback(sender, recipient, messages[-1])

            if len(messages) == 1:
                return False, None

            content = messages[-1]["content"]
            if "Code output:" not in content:
                # No code was executed.
                return False, None

            console_output = f"{Fore.MAGENTA}{content.split('Code output:')[1]} {Style.RESET_ALL}"
            print(console_output)

            if self.output_file:
                file_output = f"\n\n```yaml{content.split('Code output:')[1]}```\n\n"
                with open(self.output_file, "a", encoding="utf-8") as file:
                    file.write(file_output)

            return False, None

        kubernetes_agent.register_reply(
            [autogen.Agent, None],
            reply_func=output_message,
            config={"callback": None},
        )

        return kubernetes_agent

    def _setup_code_executor_agent(self):
        code_executor_agent = KubectlExecutorAgent(
            read_only=self.read_only,
            name="user",
            human_input_mode=self.input_mode,
            max_consecutive_auto_reply=self.max_replies,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config={
                "use_docker": False,
            },
        )

        def output_message(recipient, messages, sender, config):
            if "callback" in config and config["callback"] is not None:
                callback = config["callback"]
                callback(sender, recipient, messages[-1])

            content = messages[-1]["content"]
            if content.endswith("TERMINATE"):
                content = content.replace("TERMINATE", "")

            print(content)

            if self.output_file:
                with open(self.output_file, "a", encoding="utf-8") as file:
                    file.write(content)

            return False, None

        code_executor_agent.register_reply(
            [autogen.Agent, None],
            reply_func=output_message,
            config={"callback": None},
        )

        return code_executor_agent

    def debug(self, request):
        """Start debugging session for the given request.

        Args:
        ----
        request (str): User provided description of the problem to solve.
        """
        self.code_agent.initiate_chat(
            self.kubernetes_agent,
            silent=True,
            message=f"""
You are an expert Kubernetes administrator and your job is to resolve the issue
described below using kubectl. You are already authenticated with the cluster.

{request}

Diagnose and fix the issue using kubectl.
""",
        )
