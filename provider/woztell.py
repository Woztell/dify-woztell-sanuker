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

    #########################################################################################
    # If OAuth is supported, uncomment the following functions.
    # Warning: please make sure that the sdk version is 0.4.2 or higher.
    #########################################################################################
    # def _oauth_get_authorization_url(self, redirect_uri: str, system_credentials: Mapping[str, Any]) -> str:
    #     """
    #     Generate the authorization URL for woztell OAuth.
    #     """
    #     try:
    #         """
    #         IMPLEMENT YOUR AUTHORIZATION URL GENERATION HERE
    #         """
    #     except Exception as e:
    #         raise ToolProviderOAuthError(str(e))
    #     return ""

    # def _oauth_get_credentials(
    #     self, redirect_uri: str, system_credentials: Mapping[str, Any], request: Request
    # ) -> Mapping[str, Any]:
    #     """
    #     Exchange code for access_token.
    #     """
    #     try:
    #         """
    #         IMPLEMENT YOUR CREDENTIALS EXCHANGE HERE
    #         """
    #     except Exception as e:
    #         raise ToolProviderOAuthError(str(e))
    #     return dict()

    # def _oauth_refresh_credentials(
    #     self, redirect_uri: str, system_credentials: Mapping[str, Any], credentials: Mapping[str, Any]
    # ) -> OAuthCredentials:
    #     """
    #     Refresh the credentials
    #     """
    #     return OAuthCredentials(credentials=credentials, expires_at=-1)
