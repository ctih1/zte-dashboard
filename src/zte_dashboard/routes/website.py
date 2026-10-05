from fastapi import APIRouter, Request, Header, Depends, Response
from zte_wrapper.wrapper import ZTEWrapper
from zte_wrapper.types import PortRange, PortforwardingRule, RuleType
import json
import dataclasses
from typing import Any, Callable
import os


def craft_response(page: str) -> Response:

    with open(f"src/zte_dashboard/pages/{page}", "r", encoding="UTF-8") as f:
        html = f.read()

    return Response(html, 200)


def make_api_route(page: str) -> Callable[..., Response]:
    def r():
        return craft_response(page)

    return r


class Website:
    def __init__(self) -> None:
        pass

        self.router = APIRouter()
        self.router.add_api_route("/", make_api_route("index.html"))
        self.router.add_api_route(
            "/portforwarding", make_api_route("portforwarding.html")
        )
        self.router.add_api_route("/frii.css", make_api_route("frii.css"))
