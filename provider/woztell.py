import json
import requests
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderOAuthError


class WoztellProvider(ToolProvider):

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        pass
    
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """

            url = "https://open.api.woztell.com/v3"
            access_token = credentials.get("access_token")

            payload = {
                "query": """
                query getChannels($first: IntMax100) {
                    apiViewer {
                    channels(first: $first) {
                        edges {
                            node {
                                _id
                            }
                        }
                    }
                    }
                }
                """,
                "variables": {"first": 1},
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = requests.request(
                "POST", url, headers=headers, data=json.dumps(payload)
            )
            data = response.json()
            if data.get("errors"):
                raise ToolProviderOAuthError(str(data.get("errors")))

        except Exception as e:
            raise ToolProviderOAuthError(str(e))

