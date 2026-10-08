"""
Base Agent Abstract Class and Multi-Agent Message Bus
"""

import asyncio
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime
from core.models import AgentMessage


class AgentMessageBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[AgentMessage], None]]] = {}
        self.message_history: List[AgentMessage] = []

    def subscribe(self, topic: str, handler: Callable[[AgentMessage], None]):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    def publish(self, message: AgentMessage):
        self.message_history.append(message)
        if len(self.message_history) > 200:
            self.message_history.pop(0)

        # Topic matches receiver_agent or broadcast "*"
        if message.receiver_agent in self._subscribers:
            for handler in self._subscribers[message.receiver_agent]:
                try:
                    handler(message)
                except Exception as e:
                    print(f"Error in agent subscriber: {e}")

        if "*" in self._subscribers and message.receiver_agent != "*":
            for handler in self._subscribers["*"]:
                try:
                    handler(message)
                except Exception as e:
                    print(f"Error in broadcast subscriber: {e}")


class BaseAgent:
    def __init__(self, agent_id: str, agent_name: str, fog_node_id: str, bus: AgentMessageBus):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.fog_node_id = fog_node_id
        self.bus = bus
        self.state = "IDLE"  # IDLE, PROCESSING, ALERTING, SCALING
        self.processed_count = 0
        self.bus.subscribe(self.agent_id, self.on_message)

    def on_message(self, message: AgentMessage):
        """Handler to be overridden by subclasses."""
        pass

    def send_message(self, receiver: str, action: str, payload: Dict[str, Any]):
        msg = AgentMessage(
            message_id=f"MSG_{int(datetime.now().timestamp()*1000)}_{self.agent_id}",
            sender_agent=self.agent_id,
            receiver_agent=receiver,
            action=action,
            payload=payload,
            timestamp=datetime.now().timestamp()
        )
        self.bus.publish(msg)

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "fog_node_id": self.fog_node_id,
            "state": self.state,
            "processed_count": self.processed_count
        }
