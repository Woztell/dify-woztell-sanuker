import json
from collections.abc import Generator
from typing import Any

import requests
import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WoztellGetConversationHistoryTool(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:

        if "access_token" not in self.runtime.credentials:
            yield self.create_text_message("WOZTELL API Access Token is required.")

        access_token = self.runtime.credentials.get("access_token")
        channelId = tool_parameters.get("channelId", "")
        externalId = tool_parameters.get("externalId", "")
        limit = tool_parameters.get("limit", 100)
        after = tool_parameters.get("cursor", "")
        date_from = tool_parameters.get("from", "")
        date_to = tool_parameters.get("to", "")

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }

            member_payload = json.dumps(
                {
                    "query": """
query getMemberId($channelId: ID, $externalId: ID) {
  apiViewer {
    member(channelId: $channelId, externalId: $externalId) {
      _id
    }
  }
}
""",
                    "variables": {"channelId": channelId, "externalId": externalId},
                }
            )

            api_domain = "https://open.api.woztell.com/v3"

            member_res = requests.request(
                method="POST",
                headers=headers,
                url=f"{api_domain}",
                data=member_payload,
            )
            member_res.raise_for_status()
            memberId = ""
            member_response_data = member_res.json()
            if member_response_data.get("data")["apiViewer"]["member"] is not None:
                memberId = member_response_data.get("data")["apiViewer"]["member"][
                    "_id"
                ]
            else:
                yield self.create_text_message("member is not found")
                return

            payload = json.dumps(
                {
                    "query": """
                    query getConversationHistory(
  $channelId: String
  $memberId: String
  $last: IntMax100
  $before: String
  $from: Long
  $to: Long
) {
  apiViewer {
    conversationHistory(
      channelId: $channelId
      memberId: $memberId
      last: $last
      before: $before
      from: $from
      to: $to
    ) {
      edges {
        node {
          _id
          messageEvent
          id
          createdAt
          updatedAt
          sentAt
          readAt
          deliveredAt
          deletedAt
          from
          member {
            name
          }
          memberId
          errors
          failedAt
          platform
          channelId
          tags
          meta
          etag
          isMultipleParty
        }
      }
      pageInfo {
        hasPreviousPage
        startCursor
      }
    }
  }
}
                    """,
                    "variables": {
                        "last": limit,
                        "memberId": memberId,
                        "channelId": channelId,
                        "before": after,
                        "from": convertTime(date_from),
                        "to": convertTime(date_to),
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
            yield self.create_json_message(response_data.get("data")["apiViewer"])
        except requests.exceptions.HTTPError as e:
            yield self.create_text_message(
                f"Request error status: {e.response.status_code}, {e}"
            )
        except Exception as e:
            yield self.create_text_message(f"Error: {e}")


def convertTime(datetime: str) -> int:
    if datetime:
        time_arr = time.strptime(datetime, "%Y-%m-%d %H:%M:%S")
        return int(time.mktime(time_arr)) * 1000
    return 0
