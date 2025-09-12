import json
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WoztellGetMembersByTagsTool(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:

        if "access_token" not in self.runtime.credentials:
            yield self.create_text_message("WOZTELL API Access Token is required.")

        access_token = self.runtime.credentials.get("access_token")
        channelId = tool_parameters.get("channelId", "")
        input_tags = tool_parameters.get("tags", "")
        tags = input_tags.split(",")
        limit = tool_parameters.get("limit", 100)
        after = tool_parameters.get("cursor", "")

        if limit > 100 or limit < 1:
            yield self.create_text_message(
                f"Variable 'limit' got invalid value {limit}."
            )
            return

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            payload = json.dumps(
                {
                    "query": """
                    query getMembers(
  $first: IntMax100
  $channelId: String
  $tagFilters: [TagFilter]
  $after: String
) {
  apiViewer {
    members(first: $first, channelId: $channelId, tagFilters: $tagFilters, after: $after) {
      edges {
        node {
          _id
          externalId
          name
          tags
        }
      }
      pageInfo {
        hasNextPage
        totalCount
        endCursor
      }
    }
  }
}

                    """,
                    "variables": {
                        "first": limit,
                        "tagFilters": [{"operator": "IN", "tags": tags}],
                        "channelId": channelId,
                        "after": after,
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
