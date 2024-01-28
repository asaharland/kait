"""Kubectl executor agent tests."""
from unittest.mock import MagicMock
from kait.kubectl_executor_agent import KubectlExecutorAgent


def test_execute_code_blocks_when_read_only_then_allow_read_execution():
    """Allow read commands when read_only=False."""
    executor_agent = KubectlExecutorAgent(
        name="test_kait",
        read_only=True,
        code_execution_config={
            "use_docker": False,
        },
    )

    executor_agent.run_code = MagicMock(return_value=(0, "", ""))

    code_blocks = [("bash", "kubectl get deployment nginx")]

    executor_agent.execute_code_blocks(code_blocks=code_blocks)
    assert executor_agent.run_code.called


def test_execute_code_blocks_when_read_only_then_prevent_create_execution():
    """Prevent CUD commands when read_only=True."""
    executor_agent = KubectlExecutorAgent(
        name="test_kait",
        read_only=True,
        code_execution_config={
            "use_docker": False,
        },
    )

    code_blocks = [("bash", "kubectl create deployment nginx --image nginx")]

    exitcode, _ = executor_agent.execute_code_blocks(code_blocks=code_blocks)
    assert exitcode == 1


def test_execute_code_blocks_when_not_read_only_then_allow_create_execution():
    """Allow CRUD commands when read_only=False."""
    executor_agent = KubectlExecutorAgent(
        name="test_kait",
        read_only=False,
        code_execution_config={
            "use_docker": False,
        },
    )

    executor_agent.run_code = MagicMock(return_value=(0, "", ""))

    code_blocks = [("bash", "kubectl create deployment nginx --image nginx")]

    executor_agent.execute_code_blocks(code_blocks=code_blocks)
    assert executor_agent.run_code.called


def test_execute_code_blocks_when_blocking_command_used_then_prevent_execution():
    """Prevent commands that block execution."""
    executor_agent = KubectlExecutorAgent(
        name="test_kait",
        read_only=False,
        code_execution_config={
            "use_docker": False,
        },
    )

    executor_agent.run_code = MagicMock(return_value=(0, "", ""))

    code_blocks = [("bash", "kubectl get deployment nginx -w")]

    executor_agent.execute_code_blocks(code_blocks=code_blocks)
    assert not executor_agent.run_code.called
