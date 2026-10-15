import json

from ai_client import llm
import os


# Fictional demonstration data.
PACKAGES = {
    "UPS12345": {
        "status": "Delayed",
        "location": "Atlanta",
        "events": [
            "Arrived at sorting facility",
            "Processing delay recorded",
            "Awaiting next movement scan",
        ],
    },
    "UPS67890": {
        "status": "Delivered",
        "location": "Dallas",
        "events": [
            "Out for delivery",
            "Delivered successfully",
        ],
    },
}


def get_package_status(package_id: str) -> dict:
    package = PACKAGES.get(package_id)

    if package is None:
        return {"found": False, "package_id": package_id}

    return {
        "found": True,
        "package_id": package_id,
        **package,
    }


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "get_package_status",
        "description": (
            "Retrieve the current status and tracking "
            "events for a package."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "package_id": {"type": "string"},
            },
            "required": ["package_id"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


def investigate_package(question: str) -> dict:
    messages = [
        {"role": "user", "content": question}
    ]

    instructions = (
        "You are a read-only logistics investigation agent. "
        "Use the package tool to obtain evidence. "
        "Never invent tracking events or root causes. "
        "Distinguish confirmed facts from hypotheses."
    )

    tool_count = 0

    for step in range(4):
        response = llm.responses.create(
            model=os.environ["AZURE_CHAT_DEPLOYMENT"],
            instructions=instructions,
            input=messages,
            tools=TOOL_DEFINITIONS,
            parallel_tool_calls=False,
        )

        messages.extend(
            item.model_dump(exclude_none=True)
            for item in response.output
        )

        calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not calls:
            return {
                "answer": response.output_text,
                "tool_calls": tool_count,
            }

        for call in calls:
            try:
                args = json.loads(call.arguments)

                if (
                    call.name != "get_package_status"
                    or not isinstance(args, dict)
                    or set(args) != {"package_id"}
                    or not isinstance(
                        args["package_id"], str
                    )
                    or len(args["package_id"]) > 100
                ):
                    result = {"error": "Invalid tool request"}
                else:
                    # Production: authorize the caller's
                    # access to this package before lookup.
                    result = get_package_status(
                        args["package_id"]
                    )

            except (ValueError, TypeError):
                result = {"error": "Invalid arguments"}

            messages.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            })

            tool_count += 1

    return {
        "answer": (
            "Investigation stopped: "
            "execution limit reached."
        ),
        "tool_calls": tool_count,
    }
