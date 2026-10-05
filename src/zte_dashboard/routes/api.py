from fastapi import APIRouter, Request, Header, Depends, Response
from zte_wrapper.wrapper import ZTEWrapper
from zte_wrapper.types import PortRange, PortforwardingRule, RuleType, PortmappingRule
import json
import dataclasses
from typing import Any
from pydantic import BaseModel


class JSONEncoderWithPortRange(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type: ignore
        if isinstance(o, PortRange):
            return [o.start, o.end]
        return super().default(o)


def craft_prometheus_string(key: str, val: Any) -> str:
    return f"# TYPE {key} gauge\n{key} {val}\n\n"


def dumps(obj: object) -> str:
    return json.dumps(obj, cls=JSONEncoderWithPortRange)


class PortforwardRule(BaseModel):
    ip_addr: str
    comment: str
    port_start: int
    port_end: int
    protocol: RuleType


class PortmapRule(BaseModel):
    ip_addr: str
    comment: str
    port_external: int
    port_internal: int
    protocol: RuleType


class API:
    def __init__(self, zte_wrapper: ZTEWrapper) -> None:
        pass

        self.zte = zte_wrapper
        self.router = APIRouter()
        self.router.add_api_route("/metrics", self.signal_strength)
        self.router.add_api_route(
            "/api/portforwarding", self.query_portforwarding_rules
        )
        self.router.add_api_route(
            "/api/portforwarding",
            self.add_portforwarding_rule,
            methods=["PUT"],
        )
        self.router.add_api_route(
            "/api/portforwarding",
            self.remove_portforwarding_rule,
            methods=["DELETE"],
        )

        self.router.add_api_route("/api/portmapping", self.query_portmapping_rules)
        self.router.add_api_route(
            "/api/portmapping",
            self.add_portmapping_rule,
            methods=["PUT"],
        )
        self.router.add_api_route(
            "/api/portmapping",
            self.remove_portmapping_rule,
            methods=["DELETE"],
        )

    async def signal_strength(self) -> Response:
        data = await self.zte.signal.get_signal_strength()
        others = await self.zte.query_items(
            [
                "wifi_chip_temp",
                "therm_pa_level",
                "therm_pa_frl_level",
                "therm_tj_level",
                "pm_sensor_pa1",
                "pm_sensor_mdm",
                "pm_modem_5g",
            ]
        )

        str_data = ""
        for k, v in (dataclasses.asdict(data) | others).items():
            str_data += craft_prometheus_string(k, v)

        return Response(
            str_data,
            200,
            media_type="text/plain",
        )

    async def query_portmapping_rules(self) -> Response:
        data = await self.zte.portmapping.get_portmap_rules()

        return Response(
            dumps(data),
            200,
            media_type="application/json",
        )

    async def add_portmapping_rule(
        self, request: Request, rule: PortmapRule
    ) -> Response:
        if request.query_params.get("test") == "y":
            return Response("ok", 200)

        success = await self.zte.portmapping.set_portmap_rule(
            PortmappingRule(
                rule.ip_addr,
                rule.comment,
                rule.port_external,
                rule.port_internal,
                rule.protocol,
            )
        )
        if not success:
            return Response("Failed to save portforwarding rule", 500)

        return Response("ok", 200)

    async def remove_portmapping_rule(
        self, request: Request, indices: list[int]
    ) -> Response:
        if request.query_params.get("test") == "y":
            return Response("ok", 200)

        success = await self.zte.portmapping.delete_portmapping_rules(indices)
        if not success:
            return Response("Failed to remove portforwarding rule", 500)

        return Response("ok", 200)

    async def query_portforwarding_rules(self) -> Response:
        data = await self.zte.portforwarding.get_port_forwarding_rules()

        return Response(
            dumps(data),
            200,
            media_type="application/json",
        )

    async def add_portforwarding_rule(
        self, request: Request, rule: PortforwardRule
    ) -> Response:
        if request.query_params.get("test") == "y":
            return Response("ok", 200)

        success = await self.zte.portforwarding.set_portforwarding_rule(
            PortforwardingRule(
                rule.ip_addr,
                rule.comment,
                PortRange(rule.port_start, rule.port_end),
                rule.protocol,
            )
        )
        if not success:
            return Response("Failed to save portforwarding rule", 500)

        return Response("ok", 200)

    async def remove_portforwarding_rule(
        self, request: Request, indices: list[int]
    ) -> Response:
        if request.query_params.get("test") == "y":
            return Response("ok", 200)

        success = await self.zte.portforwarding.delete_portforwarding_rules(indices)
        if not success:
            return Response("Failed to remove portforwarding rule", 500)

        return Response("ok", 200)
