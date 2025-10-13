import json
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WoztellRedirectMemberToNodeTool(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:

        if "access_token" not in self.runtime.credentials:
            yield self.create_text_message("WOZTELL API Access Token is required.")

        access_token = self.runtime.credentials.get("access_token")
        channelId = tool_parameters.get("channelId", "")
        recipientId = tool_parameters.get("recipientId", "")
        tree = tool_parameters.get("tree", "")
        nodeCompositeId = tool_parameters.get("nodeCompositeId", "")
        runPreAction = tool_parameters.get("runPreAction", True)
        sendResponse = tool_parameters.get("sendResponse", True)
        runPostAction = tool_parameters.get("runPostAction", True)
        input_meta = tool_parameters.get("meta", "{}")
        meta = json.loads(input_meta)

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            payload = json.dumps(
                {
                    "channelId": channelId,
                    "recipientId": recipientId,
                    "redirect": {
                        "tree": tree,
                        "nodeCompositeId": nodeCompositeId,
                        "runPreAction": runPreAction,
                        "sendResponse": sendResponse,
                        "runPostAction": runPostAction,
                    },
                    "meta": meta,
                }
            )
            api_domain = "https://bot.api.woztell.com"
            res = requests.request(
                method="POST",
                headers=headers,
                url=f"{api_domain}/redirectMemberToNode",
                data=payload,
            )
            res.raise_for_status()
            response_data = res.json()
            yield self.create_json_message(response_data)
        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(
                f"Request error status: {e.response.status_code}, {e}"
            )
        except Exception as e:
            yield self.create_text_message(f"Error: {e}")
