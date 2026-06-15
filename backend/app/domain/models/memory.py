import logging
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.domain.models.tool_result import ToolResult
from langchain.messages import AnyMessage

logger = logging.getLogger(__name__)

class Memory(BaseModel):
    """
    Memory class, defining the basic behavior of memory
    """
    messages: List[AnyMessage] = []

    def add_message(self, message: AnyMessage) -> None:
        """Add message to memory"""
        self.messages.append(message)
    
    def add_messages(self, messages: List[AnyMessage]) -> None:
        """Add messages to memory"""
        self.messages.extend(messages)

    def get_messages(self) -> List[AnyMessage]:
        """Get all message history"""
        return self.messages
    
    def get_last_message(self) -> Optional[AnyMessage]:
        """Get the last message"""
        if len(self.messages) > 0:  
            return self.messages[-1]
        return None
    
    def roll_back(self) -> None:
        """Roll back memory"""
        self.messages = self.messages[:-1]
    
    # All browser tool names whose large result payloads should be stripped
    # after a step completes. Only the most recent call of each is kept intact.
    _BROWSER_TOOLS_TO_COMPACT = {
        "browser_view",
        "browser_navigate",
        "browser_click",
        "browser_input",
        "browser_scroll_up",
        "browser_scroll_down",
        "browser_move_mouse",
        "browser_press_key",
        "browser_select_option",
        "browser_open_tab",
        "browser_switch_tab",
        "browser_restart",
        # New tools added in browser agent v2
        "browser_detect_captcha",
        "browser_check_page_health",
        "browser_get_downloads",
        "browser_wait_for_download",
        "browser_iframe_content",
        "browser_iframe_click",
        "browser_handle_dialog",
        "browser_scroll_and_wait",
        "browser_reset_viewport",
    }

    def compact(self) -> None:
        """Compact memory — three-pass cleanup to keep context size small:

        Pass 1 — Browser ToolMessage payloads:
            Strip large DOM/page-state results from all but the most recent
            call of each browser tool.  The agent only needs the latest state.

        Pass 2 — Vision image_url base64 in HumanMessages:
            Vision images (user attachments, step-start screenshots) are
            embedded as data-URI base64 strings (~150-300 KB each) inside
            multimodal HumanMessage content lists.  Once the LLM has processed
            them they are never needed again, but they accumulate across steps
            and inflate every subsequent API request.  This pass strips all
            image_url entries from every HumanMessage, preserving only the
            text parts.  This is the primary cause of 500 "payload too large"
            errors on long browser automation tasks.

        Pass 3 — Browser screenshot base64 in ToolMessages:
            Browser tools return screenshots as base64 in multimodal ToolMessage
            content lists.  Strip them from all but the most recent screenshot-
            bearing ToolMessage so the agent still has the latest visual context.
        """
        # --- Pass 1: strip old browser ToolMessage payloads (existing logic) ---
        last_index: dict[str, int] = {}
        for i, message in enumerate(self.messages):
            if message.type == "tool" and message.name in self._BROWSER_TOOLS_TO_COMPACT:
                last_index[message.name] = i

        for i, message in enumerate(self.messages):
            if message.type == "tool" and message.name in self._BROWSER_TOOLS_TO_COMPACT:
                if last_index.get(message.name) == i:
                    continue
                message.content = ToolResult(success=True, data="(removed)").model_dump_json()
                logger.debug(f"Compacted tool result from memory: {message.name} at index {i}")

        # --- Pass 2: strip base64 image_url data from HumanMessages ---
        for i, message in enumerate(self.messages):
            if message.type != "human":
                continue
            if not isinstance(message.content, list):
                continue
            has_image = any(
                isinstance(part, dict) and part.get("type") == "image_url"
                for part in message.content
            )
            if not has_image:
                continue
            text_parts = [
                part for part in message.content
                if isinstance(part, dict) and part.get("type") == "text"
            ]
            if text_parts:
                message.content = (
                    text_parts[0]["text"] if len(text_parts) == 1 else text_parts
                )
            else:
                message.content = "(image removed)"
            logger.debug(f"Stripped vision image(s) from HumanMessage at index {i}")

        # --- Pass 3: strip screenshot base64 from ToolMessages (browser vision) ---
        # Keep only the most recent screenshot-bearing ToolMessage intact.
        last_screenshot_index = -1
        for i, message in enumerate(self.messages):
            if message.type != "tool":
                continue
            if not isinstance(message.content, list):
                continue
            has_screenshot = any(
                isinstance(part, dict) and part.get("type") == "image_url"
                for part in message.content
            )
            if has_screenshot:
                last_screenshot_index = i

        for i, message in enumerate(self.messages):
            if message.type != "tool":
                continue
            if not isinstance(message.content, list):
                continue
            if i == last_screenshot_index:
                continue
            text_parts = [
                part for part in message.content
                if isinstance(part, dict) and part.get("type") == "text"
            ]
            img_parts = [
                part for part in message.content
                if isinstance(part, dict) and part.get("type") == "image_url"
            ]
            if img_parts:
                message.content = text_parts[0]["text"] if (len(text_parts) == 1) else (text_parts if text_parts else "(screenshot removed)")
                logger.debug(f"Stripped browser screenshot from ToolMessage at index {i}")

        # --- Pass 4: truncate large non-browser ToolMessage results ---
        # MCP/market-data tool results can be very large. After a step completes,
        # keep only the last _MAX_TOOL_RESULT_CHARS characters of each result so
        # that accumulated step context does not flood subsequent steps and cause
        # the model to skip tool calls in favour of "known" data.
        _MAX_TOOL_RESULT_CHARS = 3000
        for i, message in enumerate(self.messages):
            if message.type != "tool":
                continue
            if message.name in self._BROWSER_TOOLS_TO_COMPACT:
                continue
            if not isinstance(message.content, str):
                continue
            if len(message.content) > _MAX_TOOL_RESULT_CHARS:
                message.content = message.content[-_MAX_TOOL_RESULT_CHARS:]
                logger.debug(
                    f"Truncated large tool result in memory: {message.name} at index {i} "
                    f"to last {_MAX_TOOL_RESULT_CHARS} chars"
                )

    @property
    def empty(self) -> bool:
        """Check if memory is empty"""
        return len(self.messages) == 0
