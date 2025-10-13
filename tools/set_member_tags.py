import json
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WoztellSetMemberTagsTool(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:

        if "access_token" not in self.runtime.credentials:
            yield self.create_text_message("WOZTELL API Access Token is required.")

        access_token = self.runtime.credentials.get("access_token")
        channelId = tool_parameters.get("channelId", "")
        input_tags = tool_parameters.get("tags", "")
        tags = input_tags.split(",")
        externalId = tool_parameters.get("externalId", "")

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            payload = json.dumps(
                {
                    "query": """
mutation AddMemberTags($input: ModifyMemberTagsInput!) {
  addMemberTags(input: $input) {
    err_code
    member {
      _id
      externalId
    }
    memberId
    ok
  }
}
                    """,
                    "variables": {
                        "input": {
                            "channel": channelId,
                            "tags": tags,
                            "externalId": externalId,
                        }
                    },
                }
            )

            api_domain = "https://open.api.woztell.com/v3"
            res = requests.request(
                method="POST",
                headers=headers,
                url=f"{api_domain}",
                data=payload,
            )
            res.raise_for_status()
            response_data = res.json()
            yield self.create_json_message(response_data.get("data"))
        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(
                f"Request error status: {e.response.status_code}, {e}"
            )
        except Exception as e:
            yield self.create_text_message(f"Error: {e}")
