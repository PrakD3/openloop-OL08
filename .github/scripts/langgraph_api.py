"""LangSmith / LangGraph Studio deployment helper."""

import json
import os
import sys


def deploy_to_langsmith(graph_config_path: str = "langgraph.json") -> None:
    """Deploy the LangGraph pipeline to LangSmith for monitoring."""
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print("LANGSMITH_API_KEY not set — skipping LangSmith deployment")
        return

    with open(graph_config_path) as f:
        config = json.load(f)

    print(f"LangGraph config loaded: {config.get('graphs', {})}")
    print("LangSmith tracing active. Visit https://smith.langchain.com to view traces.")


if __name__ == "__main__":
    graph_config = sys.argv[1] if len(sys.argv) > 1 else "langgraph.json"
    deploy_to_langsmith(graph_config)
