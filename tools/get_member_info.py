import json
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WoztellGetMemberInfoTool(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:

        if "access_token" not in self.runtime.credentials:
            yield self.create_text_message("WOZTELL API Access Token is required.")

        access_token = self.runtime.credentials.get("access_token")
        channelId = tool_parameters.get("channelId", "")
        externalId = tool_parameters.get("externalId", "")

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }

            api_domain = "https://open.api.woztell.com/v3"
            payload = json.dumps(
                {
                    "query": """
                    query getMemberInfo($channelId: ID, $externalId: ID) {
  apiViewer {
    member(channelId: $channelId, externalId: $externalId) {
      _id
      createdAt
      updatedAt
      channelId
      platform
      tags
      meta
      externalId
      botMeta {
        subscribe
        liveChat
        treeId
        nodeCompositeId
        tree {
          name
        }
        node {
          name
        }
      }
      name
      firstName
      lastName
      gender
      customLocale
      locale
      email
    }
  }
}
                    """,
                    "variables": {
                        "externalId": externalId,
                        "channelId": channelId,
                    },
                }
            )

            res = requests.request(
                method="POST",
                headers=headers,
                url=f"{api_domain}",
                data=payload,
            )
            res.raise_for_status()
            response_data = res.json()
            if response_data.get("errors"):
                yield self.create_text_message(
                    f"An error occurred while processing the data: {response_data.errors}"
                )
                return
            yield self.create_json_message(response_data.get("data")["apiViewer"])
        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(
                f"Request error status: {e.response.status_code}, {e}"
            )
        except Exception as e:
            yield self.create_text_message(f"Error: {e}")
