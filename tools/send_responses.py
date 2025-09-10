import ast
import json
from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WoztellSendResponsesTool(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """

        if "access_token" not in self.runtime.credentials:
            yield self.create_text_message("WOZTELL API Access Token is required.")

        access_token = self.runtime.credentials.get("access_token")
        channelId = tool_parameters.get("channelId", "")
        recipientId = tool_parameters.get("recipientId", "")
        input_response = tool_parameters.get("response", "{}")
        input_response = repr(input_response).strip("'")

        try:
            response_obj = ast.literal_eval(input_response)
            if not response_obj or type(response_obj) is not dict:
                yield self.create_text_message("Response is required.")

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            payload = json.dumps(
                {
                    "channelId": channelId,
                    "recipientId": recipientId,
                    "response": [response_obj],
                }
            )
            api_domain = "https://bot.api.woztell.com"
            res = requests.request(
                method="POST",
                headers=headers,
                url=f"{api_domain}/sendResponses",
                data=payload,
            )
            res.raise_for_status()
            response_data = res.json()
            yield self.create_json_message(response_data)
        except (ValueError, SyntaxError):
            yield self.create_text_message(
                "Response is required and is in json format."
            )
        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(
                f"Request error status: {e.response.status_code}, {e}"
            )
        except Exception as e:
            yield self.create_text_message(f"Error: {e}")
