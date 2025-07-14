# core/loop.py - Stock Stability Checker Agent Loop

import asyncio
from ..modules.perception import run_perception
from ..modules.decision import generate_plan
from ..modules.action import run_python_sandbox
from ..modules.model_manager import ModelManager
from .session import MultiMCP
from .strategy import select_decision_prompt_path
from .context import AgentContext
from ..modules.tools import summarize_tools
import re

try:
    from ..agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")

class AgentLoop:
    def __init__(self, context: AgentContext):
        self.context = context
        self.mcp = self.context.dispatcher
        # Initialize model manager with AI configuration
        ai_config = self.context.agent_profile.llm_config
        self.model = ModelManager(ai_config)

    async def run(self):
        max_steps = self.context.agent_profile.strategy.max_steps

        for step in range(max_steps):
            print(f"📊 Step {step+1}/{max_steps} - Stock Analysis in Progress...")
            self.context.step = step
            lifelines_left = self.context.agent_profile.strategy.max_lifelines_per_step

            while lifelines_left > 0:  # Changed from >= 0 to > 0
                # === Perception ===
                user_input_override = getattr(self.context, "user_input_override", None)
                perception = await run_perception(
                    context=self.context, 
                    user_input=user_input_override or self.context.user_input
                )

                print(f"[perception] {perception}")

                selected_servers = perception.selected_servers
                selected_tools = self.mcp.get_tools_from_servers(selected_servers)
                if not selected_tools:
                    log("loop", "⚠️ No tools selected — aborting step.")
                    break

                # === Planning ===
                tool_descriptions = summarize_tools(selected_tools)
                prompt_path = select_decision_prompt_path(
                    planning_mode=self.context.agent_profile.strategy.planning_mode,
                    exploration_mode=self.context.agent_profile.strategy.exploration_mode,
                )

                plan = await generate_plan(
                    user_input=self.context.user_input,
                    perception=perception,
                    memory_items=self.context.memory.get_session_items(),
                    tool_descriptions=tool_descriptions,
                    prompt_path=prompt_path,
                    step_num=step + 1,
                    max_steps=max_steps,
                    context=self.context,
                    model_manager=self.model  # Pass existing ModelManager instance
                )
                print(f"[plan] {plan}")

                # === Execution ===
                if re.search(r"^\s*(async\s+)?def\s+solve\s*\(", plan, re.MULTILINE):
                    print("[loop] Detected solve() plan — running sandboxed...")

                    self.context.log_subtask(tool_name="solve_sandbox", status="pending")
                    result = await run_python_sandbox(plan, dispatcher=self.mcp)

                    success = False
                    if isinstance(result, str):
                        result = result.strip()
                        if result.startswith("FINAL_ANSWER:"):
                            success = True
                            self.context.final_answer = result
                            self.context.update_subtask_status("solve_sandbox", "success")
                            self.context.memory.add_tool_output(
                                tool_name="solve_sandbox",
                                tool_args={"plan": plan},
                                tool_result={"result": result},
                                success=True,
                                tags=["sandbox", "stock_analysis"],
                            )
                            return {"status": "done", "result": self.context.final_answer}
                        elif result.startswith("FURTHER_PROCESSING_REQUIRED:"):
                            content = result.split("FURTHER_PROCESSING_REQUIRED:")[1].strip()
                            self.context.user_input_override = (
                                f"Original stock analysis task: {self.context.user_input}\n\n"
                                f"Your last analysis produced this result:\n\n"
                                f"{content}\n\n"
                                f"If this fully answers the stock stability question, return:\n"
                                f"FINAL_ANSWER: your recommendation with reasoning\n\n"
                                f"Otherwise, return the next FUNCTION_CALL to continue analysis."
                            )
                            log("loop", f"📨 Forwarding stock analysis result to next step:\n{self.context.user_input_override}\n\n")
                            log("loop", f"🔁 Continuing stock analysis — Step {step+1} continues...")
                            break  # Step will continue
                        elif result.startswith("[sandbox error:"):
                            success = False
                            self.context.final_answer = "FINAL_ANSWER: [Stock analysis failed due to execution error]"
                        else:
                            success = True
                            self.context.final_answer = f"FINAL_ANSWER: {result}"
                    else:
                        self.context.final_answer = f"FINAL_ANSWER: {result}"

                    if success:
                        self.context.update_subtask_status("solve_sandbox", "success")
                    else:
                        self.context.update_subtask_status("solve_sandbox", "failure")

                    self.context.memory.add_tool_output(
                        tool_name="solve_sandbox",
                        tool_args={"plan": plan},
                        tool_result={"result": result},
                        success=success,
                        tags=["sandbox", "stock_analysis"],
                    )

                    if success and "FURTHER_PROCESSING_REQUIRED:" not in result:
                        return {"status": "done", "result": self.context.final_answer}
                    else:
                        lifelines_left -= 1
                        log("loop", f"🛠 Retrying stock analysis... Lifelines left: {lifelines_left}")
                        if lifelines_left <= 0:
                            log("loop", "❌ No lifelines remaining - terminating analysis")
                            self.context.final_answer = "FINAL_ANSWER: [Analysis terminated - max retries exceeded]"
                            return {"status": "done", "result": self.context.final_answer}
                        continue
                else:
                    lifelines_left -= 1
                    log("loop", f"⚠️ Invalid plan detected — retrying... Lifelines left: {lifelines_left}")
                    if lifelines_left <= 0:
                        log("loop", "❌ No lifelines remaining - terminating analysis")
                        self.context.final_answer = "FINAL_ANSWER: [Analysis terminated - max retries exceeded]"
                        return {"status": "done", "result": self.context.final_answer}
                    continue
            
            # If we exit the lifelines loop without success, terminate
            if lifelines_left <= 0:
                log("loop", "❌ Step failed - no lifelines remaining")
                self.context.final_answer = "FINAL_ANSWER: [Analysis failed - max retries exceeded in step]"
                return {"status": "done", "result": self.context.final_answer}

        log("loop", "⚠️ Max steps reached without completing stock analysis.")
        self.context.final_answer = "FINAL_ANSWER: [Stock analysis incomplete - max steps reached]"
        return {"status": "done", "result": self.context.final_answer} 