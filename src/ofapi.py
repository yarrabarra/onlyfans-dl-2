import requests
import hashlib
import click
from util import get_session_config


from typing import Callable, Type, Literal, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse
from loguru import logger as log

from apiclient import APIClient, endpoint
from apiclient.request_strategies import RequestStrategy
from apiclient.response_handlers import JsonResponseHandler
from apiclient.response import Response
from apiclient.utils.typing import OptionalDict

from models.messages import MessageList, Message
from models.purchase import Purchase
from models.profile import Profile
from models.post import Post
from models.subscriptions import Subscription

DYNAMIC_RULE_URL = "https://raw.githubusercontent.com/DIGITALCRIMINALS/dynamic-rules/main/onlyfans.json"
POST_LIMIT = 50

# Type Alias
Offsetables = Subscription | Purchase | Post | MessageList


def to_str(item: str | int | float):
    """Needed as floats are expected with six digit precision in API response"""
    if isinstance(item, str):
        return item
    elif isinstance(item, float):
        return "{:.6f}".format(item)
    return str(item)


@click.pass_context
def get_max_days_offset(ctx):
    max_post_days_value = ctx.params["max_post_days"]
    delta = (datetime.today() - timedelta(max_post_days_value)).timestamp()
    return delta // 1  # cheap floor that retains float


@endpoint(base_url="https://onlyfans.com/api2/v2")
class Endpoint:
    posts = "/users/{id}/posts"
    archived = "/users/{id}/posts/archived"
    stories = "/users/{id}/stories"
    messages = "/chats/{id}/messages"
    purchased = "/posts/paid"
    profile = "/users/{id}"
    subscriptions = "/subscriptions/subscribes"


class SignedRequestsStrategy(RequestStrategy):
    """Requests strategy that uses a signed header"""

    session_vars = None

    def _configure_headers(
        self,
    ):
        if self.session_vars is None:
            try:
                session_vars = get_session_config()
            except ValueError as e:
                log.critical(f"Config error: {e}")
                raise
            self.dynamic_rules = None
            self.api_headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "app-token": "33d57ade8c02dbc5a333db99ff9ae26a",
                "User-Agent": session_vars["USER_AGENT"],
                "x-bc": str(session_vars["X_BC"]),
                "user-id": str(session_vars["USER_ID"]),
                "Cookie": f"auh_id={str(session_vars['USER_ID'])}; sess={session_vars['SESS_COOKIE']}",
            }
            self.session_vars = session_vars

        # Get the rules for the signed headers dynamically, so we don't have to update the script every time they change
        if self.dynamic_rules is None:
            self.dynamic_rules = requests.get(DYNAMIC_RULE_URL).json()

    def set_client(self, client: "APIClient"):
        super().set_client(client)
        self._configure_headers()
        # Set a global `requests.session` on the parent client instance.
        if self.get_session() is None:
            self.set_session(requests.session())

    def _make_request(
        self,
        request_method: Callable,
        endpoint: str,
        params: OptionalDict = None,
        headers: OptionalDict = None,
        data: OptionalDict = None,
        **kwargs,
    ) -> Response:
        """Inject a signed header into the request and delegate the rest back to the superclass"""
        if headers is None:
            headers = {}
        headers.update(self.api_headers)
        headers.update(self._create_signed_headers(endpoint, params))
        return super()._make_request(request_method, endpoint, params, headers, data, **kwargs)

    def _create_signed_headers(self, endpoint, queryParams: dict | None):
        if self.session_vars is None:
            raise Exception("Session vars did not fully load, aborting.")
        if self.dynamic_rules is None:
            raise Exception("Dynamic rules did not fully load, aborting.")
        path = urlparse(endpoint).path
        if queryParams:
            query = "&".join("=".join((key, str(val))) for (key, val) in queryParams.items())
            path = f"{path}?{query}"
        unixtime = str(int(datetime.now().timestamp()))
        msg = "\n".join([self.dynamic_rules["static_param"], unixtime, path, self.session_vars["USER_ID"]])
        hash_object = hashlib.sha1(msg.encode("utf-8"))
        sha_1_sign = hash_object.hexdigest()
        sha_1_b = sha_1_sign.encode("ascii")
        checksum = (
            sum([sha_1_b[number] for number in self.dynamic_rules["checksum_indexes"]])
            + self.dynamic_rules["checksum_constant"]
        )
        return {"sign": self.dynamic_rules["format"].format(sha_1_sign, abs(checksum)), "time": unixtime}


class OFClient(APIClient):
    def __init__(self, **kwargs):
        self.request_strategy = SignedRequestsStrategy()
        super().__init__(request_strategy=self.request_strategy, response_handler=JsonResponseHandler, **kwargs)

    def get_request_timeout(self):
        return 120.0  # Good things can take a while

    def _get_by_offset(
        self,
        endpoint,
        itemType: Type[Offsetables],
        pageType: Literal["offset", "afterPublishTime", "id"],
        paramOverride: dict[str, str | int] | None = None,
        items: list[Offsetables] | None = None,
        pageOffset: int | float = 0,
    ) -> list[Any]:
        # TODO: Got to be a cleaner way to do this

        getParams = {"limit": POST_LIMIT, "order": "desc"}
        if paramOverride is not None:
            getParams.update(paramOverride)

        if items is None:
            items = []
        if pageOffset > 0:
            getParams[pageType] = to_str(pageOffset)

        log.debug(f"Fetching endpoint {endpoint} - {pageType}: {pageOffset}")
        request = self.get(endpoint, getParams)
        if isinstance(request, dict):
            base_list = [itemType.model_validate(request)]
        else:
            base_list = [itemType.model_validate(item) for item in request]

        items.extend(base_list)
        # Recursive query
        if len(base_list) >= POST_LIMIT:
            if pageType == "offset":
                pageOffset += POST_LIMIT
            elif pageType == "afterPublishTime":
                if not isinstance(items[-1], Post):
                    raise ValueError("Incorrect value used")
                pageOffset = float(items[-1].postedAtPrecise)
            elif pageType == "id":
                if not isinstance(items[-1], MessageList):
                    raise ValueError("Incorrect value used")
                if not items[-1].hasMore:
                    return items
                pageOffset = items[-1].list[-1].id
            items.extend(self._get_by_offset(endpoint, itemType, pageType, paramOverride, items, pageOffset))
        return items

    def get_subscriptions(self) -> list[Subscription]:
        return self._get_by_offset(Endpoint.subscriptions, Subscription, "offset", {"type": "active"})

    def get_purchases(self) -> list[Purchase]:
        return self._get_by_offset(Endpoint.purchased, Purchase, "offset")

    def get_posts(self, subscription: Subscription) -> list[Post]:
        pageOffset = get_max_days_offset()
        return self._get_by_offset(
            Endpoint.posts.format(id=subscription.id),
            Post,
            "afterPublishTime",
            {"order": "publish_date_asc"},
            pageOffset=pageOffset,
        )

    def get_messages(self, subscription: Subscription) -> list[Message]:
        results = []
        response = self._get_by_offset(Endpoint.messages.format(id=subscription.id), MessageList, "id")
        for item in response:
            if not isinstance(item, MessageList):
                raise ValueError("Incorrect type returned from query")
            results.extend(item.list)
        return results

    def get_profile(self, profile_name: str):
        # <profile_name> = "me" -> info about yourself
        response = self.get(Endpoint.profile.format(id=profile_name))
        return Profile.model_validate(response)
