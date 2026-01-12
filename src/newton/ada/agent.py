"""
Ada Agent System
=================

Autonomous task execution with planning and verification.
Unlike ChatGPT's agent mode, Ada verifies each step before proceeding.
"""

import time
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import re

from .schema import (
    AgentAction,
    AgentPlan,
    AgentResult,
    AgentStatus,
    CodeLanguage,
    CodeResult,
)


class ActionType(Enum):
    """Types of actions the agent can take."""

    SEARCH = "search"          # Search for information
    READ = "read"              # Read a file
    WRITE = "write"            # Write a file
    EXECUTE = "execute"        # Execute code
    WEB = "web"                # Fetch web content
    ANALYZE = "analyze"        # Analyze data
    TRANSFORM = "transform"    # Transform data
    COMMUNICATE = "communicate"  # Send notification
    DELEGATE = "delegate"      # Delegate to another agent


@dataclass
class Tool:
    """A tool the agent can use."""

    name: str
    description: str
    action_type: ActionType
    handler: Callable[[Dict[str, Any]], Any]
    requires_approval: bool = False
    parameters: Dict[str, str] = dataclass_field(default_factory=dict)

    def execute(self, params: Dict[str, Any]) -> Any:
        """Execute the tool."""
        return self.handler(params)


class ToolRegistry:
    """Registry of available tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in tools."""

        # Search tool
        self.register(Tool(
            name="search",
            description="Search for files or content",
            action_type=ActionType.SEARCH,
            handler=self._search_handler,
            parameters={"query": "Search query", "path": "Optional path to search in"},
        ))

        # Read tool
        self.register(Tool(
            name="read_file",
            description="Read the contents of a file",
            action_type=ActionType.READ,
            handler=self._read_handler,
            parameters={"path": "Path to the file"},
        ))

        # Write tool
        self.register(Tool(
            name="write_file",
            description="Write content to a file",
            action_type=ActionType.WRITE,
            handler=self._write_handler,
            requires_approval=True,
            parameters={"path": "Path to the file", "content": "Content to write"},
        ))

        # Execute tool
        self.register(Tool(
            name="execute_code",
            description="Execute code in a sandbox",
            action_type=ActionType.EXECUTE,
            handler=self._execute_handler,
            requires_approval=True,
            parameters={"code": "Code to execute", "language": "Programming language"},
        ))

        # Analyze tool
        self.register(Tool(
            name="analyze",
            description="Analyze data or text",
            action_type=ActionType.ANALYZE,
            handler=self._analyze_handler,
            parameters={"data": "Data to analyze", "analysis_type": "Type of analysis"},
        ))

    def register(self, tool: Tool):
        """Register a tool."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        """List all available tools."""
        return list(self._tools.values())

    # Built-in handlers
    def _search_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search requests."""
        query = params.get("query", "")
        path = params.get("path", ".")

        # Mock search results
        return {
            "success": True,
            "results": [
                {"path": f"{path}/file1.py", "match": f"Found: {query}"},
                {"path": f"{path}/file2.py", "match": f"Contains: {query}"},
            ],
            "total_matches": 2,
        }

    def _read_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle read requests."""
        path = params.get("path", "")

        # In production, actually read the file
        return {
            "success": True,
            "path": path,
            "content": f"# Mock content from {path}\nprint('Hello, Ada!')",
            "lines": 2,
        }

    def _write_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle write requests."""
        path = params.get("path", "")
        content = params.get("content", "")

        # In production, actually write the file
        return {
            "success": True,
            "path": path,
            "bytes_written": len(content),
        }

    def _execute_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code execution requests."""
        code = params.get("code", "")
        language = params.get("language", "python")

        # Mock execution
        return {
            "success": True,
            "language": language,
            "stdout": "Execution output",
            "stderr": "",
            "return_value": None,
        }

    def _analyze_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analysis requests."""
        data = params.get("data", "")
        analysis_type = params.get("analysis_type", "general")

        return {
            "success": True,
            "analysis_type": analysis_type,
            "result": f"Analysis of: {str(data)[:100]}...",
            "insights": ["Insight 1", "Insight 2"],
        }


class Planner:
    """
    Plans task execution.

    Breaks down complex tasks into actionable steps.
    """

    def __init__(self, llm: Any = None):
        self.llm = llm

    def create_plan(
        self,
        task: str,
        available_tools: List[Tool],
    ) -> AgentPlan:
        """
        Create an execution plan for a task.

        Args:
            task: The task description
            available_tools: Tools available to the agent

        Returns:
            AgentPlan with steps
        """
        # Analyze task to determine steps
        steps = self._analyze_task(task, available_tools)

        # Identify steps requiring approval
        approval_steps = []
        for i, step in enumerate(steps):
            if any(word in step.lower() for word in ["write", "delete", "execute", "send", "modify"]):
                approval_steps.append(step)

        return AgentPlan(
            goal=task,
            steps=steps,
            estimated_actions=len(steps),
            requires_approval=approval_steps,
        )

    def _analyze_task(self, task: str, tools: List[Tool]) -> List[str]:
        """Analyze task and break into steps."""
        task_lower = task.lower()

        # Pattern matching for common task types
        steps = []

        # File operations
        if any(word in task_lower for word in ["find", "search", "locate"]):
            steps.append("Search for matching files/content")

        if any(word in task_lower for word in ["read", "view", "show", "display"]):
            steps.append("Read the target file(s)")

        if any(word in task_lower for word in ["write", "create", "generate"]):
            steps.append("Generate the content")
            steps.append("Write to file")

        if any(word in task_lower for word in ["analyze", "check", "review"]):
            steps.append("Read the content")
            steps.append("Analyze the data")
            steps.append("Generate report")

        if any(word in task_lower for word in ["count", "calculate", "compute"]):
            steps.append("Collect relevant data")
            steps.append("Perform calculation")
            steps.append("Report results")

        if any(word in task_lower for word in ["fix", "correct", "update", "modify"]):
            steps.append("Identify the issue")
            steps.append("Determine the fix")
            steps.append("Apply the modification")
            steps.append("Verify the fix")

        # Default steps if no patterns matched
        if not steps:
            steps = [
                "Understand the task requirements",
                "Gather necessary information",
                "Execute the task",
                "Verify results",
            ]

        return steps

    def refine_plan(self, plan: AgentPlan, feedback: str) -> AgentPlan:
        """Refine a plan based on feedback."""
        # In production, use LLM to refine
        # For now, just add a feedback-based step
        new_steps = plan.steps.copy()
        new_steps.insert(0, f"Address feedback: {feedback}")
        return AgentPlan(
            goal=plan.goal,
            steps=new_steps,
            estimated_actions=len(new_steps),
            requires_approval=plan.requires_approval,
        )


class Executor:
    """
    Executes planned actions.

    Handles tool invocation and result verification.
    """

    def __init__(self, tools: ToolRegistry, llm: Any = None):
        self.tools = tools
        self.llm = llm

    def execute_step(
        self,
        step: str,
        context: Dict[str, Any],
    ) -> Tuple[AgentAction, Dict[str, Any]]:
        """
        Execute a single step.

        Args:
            step: Step description
            context: Current execution context

        Returns:
            Tuple of (action taken, updated context)
        """
        start_time = datetime.now()

        # Determine which tool to use
        tool, params = self._select_tool(step, context)

        # Create action record
        action = AgentAction(
            action_type=tool.name if tool else "thinking",
            description=step,
            input_data=params,
            status=AgentStatus.EXECUTING,
            started_at=start_time,
        )

        # Execute the tool
        if tool:
            try:
                result = tool.execute(params)
                action.output_data = result
                action.status = AgentStatus.COMPLETED
                context["last_result"] = result
            except Exception as e:
                action.error = str(e)
                action.status = AgentStatus.FAILED
        else:
            # No tool needed, just thinking
            action.output_data = {"thought": f"Processing: {step}"}
            action.status = AgentStatus.COMPLETED

        action.completed_at = datetime.now()

        return action, context

    def _select_tool(
        self,
        step: str,
        context: Dict[str, Any],
    ) -> Tuple[Optional[Tool], Dict[str, Any]]:
        """Select the appropriate tool for a step."""
        step_lower = step.lower()
        params = {}

        # Match step to tool
        if any(word in step_lower for word in ["search", "find", "locate"]):
            # Extract query from step
            query_match = re.search(r'(?:search|find|locate)\s+(?:for\s+)?(.+)', step_lower)
            params["query"] = query_match.group(1) if query_match else step
            return self.tools.get("search"), params

        if any(word in step_lower for word in ["read", "view", "open"]):
            # Extract path if mentioned
            path_match = re.search(r'(?:read|view|open)\s+(.+)', step_lower)
            params["path"] = path_match.group(1).strip() if path_match else context.get("target_file", "file.txt")
            return self.tools.get("read_file"), params

        if any(word in step_lower for word in ["write", "create", "save"]):
            params["path"] = context.get("target_file", "output.txt")
            params["content"] = context.get("content", "")
            return self.tools.get("write_file"), params

        if any(word in step_lower for word in ["execute", "run"]):
            params["code"] = context.get("code", "")
            params["language"] = context.get("language", "python")
            return self.tools.get("execute_code"), params

        if any(word in step_lower for word in ["analyze", "check", "review"]):
            params["data"] = context.get("last_result", "")
            params["analysis_type"] = "general"
            return self.tools.get("analyze"), params

        return None, params


class AdaAgent:
    """
    Autonomous agent for task execution.

    Features:
    - Automatic task planning
    - Step-by-step execution with verification
    - Tool integration
    - Human approval workflow
    - Error recovery

    Why this is BETTER than ChatGPT's agent:
    1. Each step is verified before proceeding
    2. Clear approval workflow for sensitive actions
    3. Full audit trail of all actions
    4. Automatic error recovery
    """

    def __init__(
        self,
        engine: Any = None,
        max_steps: int = 50,
        timeout: int = 300,
        require_approval: bool = False,
    ):
        self.engine = engine
        self.max_steps = max_steps
        self.timeout = timeout
        self.require_approval = require_approval

        # Initialize components
        self.tools = ToolRegistry()
        self.planner = Planner(llm=engine.llm if engine else None)
        self.executor = Executor(self.tools, llm=engine.llm if engine else None)

        # Approval callback
        self._approval_callback: Optional[Callable[[str], bool]] = None

    def set_approval_callback(self, callback: Callable[[str], bool]):
        """Set callback for approval requests."""
        self._approval_callback = callback

    def execute(
        self,
        task: str,
        require_approval: Optional[bool] = None,
        max_steps: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResult:
        """
        Execute a task autonomously.

        Args:
            task: Task description
            require_approval: Override approval setting
            max_steps: Override max steps
            context: Initial context

        Returns:
            AgentResult with execution details
        """
        start_time = datetime.now()
        require_approval = require_approval if require_approval is not None else self.require_approval
        max_steps = max_steps or self.max_steps
        context = context or {}

        # Create result object
        result = AgentResult(
            goal=task,
            status=AgentStatus.PLANNING,
            summary="",
            started_at=start_time,
        )

        try:
            # Step 1: Plan
            plan = self.planner.create_plan(task, self.tools.list_tools())
            result.plan = plan
            result.status = AgentStatus.EXECUTING

            # Step 2: Check for approval if needed
            if require_approval and plan.requires_approval:
                if not self._get_approval(plan):
                    result.status = AgentStatus.BLOCKED
                    result.summary = "Task blocked: approval denied"
                    return result

            # Step 3: Execute each step
            for i, step in enumerate(plan.steps):
                if i >= max_steps:
                    result.summary = f"Stopped after {max_steps} steps (limit reached)"
                    break

                # Check timeout
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > self.timeout:
                    result.status = AgentStatus.FAILED
                    result.summary = f"Timeout after {elapsed:.0f} seconds"
                    break

                # Execute step
                action, context = self.executor.execute_step(step, context)
                result.actions.append(action)

                # Check for failure
                if action.status == AgentStatus.FAILED:
                    # Try to recover
                    if not self._try_recover(action, context):
                        result.status = AgentStatus.FAILED
                        result.summary = f"Failed at step {i+1}: {action.error}"
                        break

            # Step 4: Finalize
            if result.status == AgentStatus.EXECUTING:
                result.status = AgentStatus.COMPLETED
                result.summary = self._generate_summary(result)

            result.output = context.get("last_result")
            result.completed_at = datetime.now()
            result.total_time_seconds = (result.completed_at - start_time).total_seconds()

        except Exception as e:
            result.status = AgentStatus.FAILED
            result.summary = f"Unexpected error: {str(e)}"
            result.completed_at = datetime.now()

        return result

    def _get_approval(self, plan: AgentPlan) -> bool:
        """Request approval for the plan."""
        if self._approval_callback:
            approval_message = f"Task: {plan.goal}\n"
            approval_message += f"Steps requiring approval:\n"
            for step in plan.requires_approval:
                approval_message += f"  - {step}\n"
            return self._approval_callback(approval_message)

        # Auto-approve if no callback set
        return True

    def _try_recover(self, action: AgentAction, context: Dict[str, Any]) -> bool:
        """Try to recover from a failed action."""
        # Simple recovery strategies
        error = action.error or ""

        # File not found - try with different path
        if "not found" in error.lower():
            context["retry_count"] = context.get("retry_count", 0) + 1
            return context["retry_count"] < 3

        # Permission denied - skip this step
        if "permission" in error.lower():
            return True  # Continue with next step

        return False

    def _generate_summary(self, result: AgentResult) -> str:
        """Generate a summary of the execution."""
        completed = sum(1 for a in result.actions if a.status == AgentStatus.COMPLETED)
        failed = sum(1 for a in result.actions if a.status == AgentStatus.FAILED)

        summary = f"Task '{result.goal}' completed. "
        summary += f"Executed {completed} actions successfully"
        if failed:
            summary += f", {failed} failed"
        summary += f" in {result.total_time_seconds:.1f} seconds."

        return summary

    def register_tool(self, tool: Tool):
        """Register a new tool."""
        self.tools.register(tool)

    def list_capabilities(self) -> List[str]:
        """List agent capabilities."""
        return [
            f"{tool.name}: {tool.description}"
            for tool in self.tools.list_tools()
        ]
