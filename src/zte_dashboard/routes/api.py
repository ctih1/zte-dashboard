from fastapi import APIRouter, Request, Header, Depends, Response, HTTPException
from zte_wrapper.wrapper import ZTEWrapper
from zte_wrapper.types import (
    PortRange,
    PortforwardingRule,
    RuleType,
    PortmappingRule,
    SMSMessage,
    PhoneNumber,
    MacBinding,
)
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


class Message(BaseModel):
    phone_number: str
    message: str


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
            methods=["POST"],
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
            methods=["POST"],
        )
        self.router.add_api_route(
            "/api/portmapping",
            self.remove_portmapping_rule,
            methods=["DELETE"],
        )

        self.router.add_api_route(
            "/api/sms",
            self.query_sms,
            methods=["GET"],
        )

        self.router.add_api_route(
            "/api/sms",
            self.send_sms,
            methods=["POST"],
        )

        self.router.add_api_route(
            "/api/devices",
            self.query_devices,
            methods=["GET"],
        )

        self.router.add_api_route(
            "/api/devices/lan",
            self.query_lan_devices,
            methods=["GET"],
        )

        self.router.add_api_route(
            "/api/devices/offline",
            self.query_offline_devices,
            methods=["GET"],
        )

        self.router.add_api_route(
            "/api/devices/wlan",
            self.query_wlan_devices,
            methods=["GET"],
        )

        self.router.add_api_route(
            "/api/devices/bindings",
            self.bind_ip,
            methods=["POST"],
        )

        self.router.add_api_route(
            "/api/devices/bindings",
            self.remove_binding,
            methods=["DELETE"],
        )

        self.router.add_api_route(
            "/api/devices/bindings",
            self.get_bindings,
            methods=["GET"],
        )

        self.router.add_api_route("/api/debug/ping", self.start_ping, methods=["POST"])
        self.router.add_api_route("/api/debug/ping", self.get_ping, methods=["GET"])
        self.router.add_api_route(
            "/api/debug/trace", self.start_traceroute, methods=["POST"]
        )
        self.router.add_api_route(
            "/api/debug/trace", self.get_traceroute, methods=["GET"]
        )
        self.router.add_api_route("/api/debug", self.clear_all, methods=["DELETE"])

    async def start_ping(self, ip: str, ping_count: int = 4, size: int = 64) -> None:
        await self.zte.network_tools.start_ping(ip, ping_count, size, ping_quiet=1)

    async def start_traceroute(self, ip: str) -> None:
        await self.zte.network_tools.start_traceroute(ip)

    async def get_ping(self) -> str:
        return await self.zte.network_tools.get_ping_output() or ""

    async def get_traceroute(self) -> str:
        return await self.zte.network_tools.get_traceroute_output() or ""

    async def clear_all(self) -> None:
        await self.zte.network_tools.clear_ping_output()
        await self.zte.network_tools.clear_traceroute_output()

    async def get_bindings(self) -> list[MacBinding]:
        return await self.zte.bindings.get_mac_bindings()

    async def remove_binding(self, mac_addr: str):
        result = await self.zte.bindings.delete_mac_binding(mac_addr)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to delete binding")

    async def bind_ip(self, ip_addr: str, mac_addr: str):
        result = await self.zte.bindings.create_mac_binding(mac_addr, ip_addr)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create binding")

    async def query_devices(self):
        wlan_devices = await self.zte.devices.get_wlan_devices()
        offline_devices = await self.zte.devices.get_offline_devices()
        lan_devices = await self.zte.devices.get_lan_devices()

        return {"offline": offline_devices, "wlan": wlan_devices, "lan": lan_devices}

    async def query_lan_devices(self):
        return await self.zte.devices.get_lan_devices()

    async def query_wlan_devices(self):
        return await self.zte.devices.get_wlan_devices()

    async def query_offline_devices(self):
        return await self.zte.devices.get_offline_devices()

    async def query_sms(self) -> dict[PhoneNumber, list[SMSMessage]]:
        messages = await self.zte.sms.get_sms()
        if not messages:
            raise HTTPException(status_code=500, detail="Could not retrieve messages")

        return messages

    async def send_sms(
        self, request: Request, message: Message, hour_offset: int = 0
    ) -> None:
        if request.query_params.get("test") == "y":
            return

        success = await self.zte.sms.send_sms(
            message.phone_number, message.message, hour_offset
        )
        if not success:
            raise HTTPException(status_code=500, detail="Could not send messages")

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
