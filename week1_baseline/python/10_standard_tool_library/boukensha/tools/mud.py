from __future__ import annotations

from typing import Any, Callable

from ..mud.primitives import Primitives
from ..mud.session import Session, SessionError


def register(registry: Any, *, host: str = "localhost", port: int = 4000, name: str, password: str, session: Session | None = None) -> Session:
    session = session or Session(host, port)
    primitives = Primitives()

    def guard() -> str | None:
        return None if session.is_open() else "error: not connected — call mud_connect first"

    def send(command: object) -> str:
        session.drain()
        session.send_command(command)
        return session.read_until_prompt()

    def gameplay(method: str, *args: object, **kwargs: object) -> str:
        blocked = guard()
        if blocked:
            return blocked
        try:
            return send(getattr(primitives, method)(*args, **kwargs))
        except (ValueError, TypeError) as exc:
            return f"error: {exc}"

    registry.tool("mud_connect", description="Open the connection and log in.", parameters={}, block=lambda: _connect(session, name, password))
    registry.tool("mud_disconnect", description="Close the MUD connection gracefully.", parameters={}, block=lambda: _disconnect(session))
    registry.tool("mud_status", description="Return whether the MUD session is connected.", parameters={}, block=lambda: f"connected to {session.host}:{session.port}" if session.is_open() else "disconnected")
    registry.tool("look", description="Look at the current room or target.", parameters={"target": {"type": "string"}, "preposition": {"type": "string"}}, block=lambda target=None, preposition=None: gameplay("look", target, preposition))
    registry.tool("examine", description="Examine a target.", parameters={"target": {"type": "string"}}, block=lambda target: gameplay("examine", target))
    registry.tool("check", description="Query character information.", parameters={"kind": {"type": "string"}}, block=lambda kind: gameplay("info_self", kind))
    registry.tool("move", description="Move in a direction.", parameters={"direction": {"type": "string"}}, block=lambda direction: gameplay("move", direction))
    registry.tool("flee", description="Flee from combat.", parameters={}, block=lambda: gameplay("flee"))
    registry.tool("set_position", description="Change body position.", parameters={"position": {"type": "string"}}, block=lambda position: gameplay("set_position", position))
    registry.tool("track", description="Track a target.", parameters={"target": {"type": "string"}}, block=lambda target: gameplay("track", target))
    registry.tool("attack", description="Attack a target.", parameters={"target": {"type": "string"}, "style": {"type": "string"}}, block=lambda target, style="kill": gameplay("attack", style, target))
    registry.tool("skill_strike", description="Use a combat skill.", parameters={"skill": {"type": "string"}, "target": {"type": "string"}}, block=lambda skill, target: gameplay("skill_strike", skill, target))
    registry.tool("consider", description="Assess a target.", parameters={"target": {"type": "string"}}, block=lambda target: gameplay("consider", target))
    registry.tool("say", description="Speak in the room.", parameters={"text": {"type": "string"}, "mode": {"type": "string"}}, block=lambda text, mode="say": gameplay("say_local", mode, text))
    registry.tool("tell", description="Message a player.", parameters={"target": {"type": "string"}, "text": {"type": "string"}, "mode": {"type": "string"}}, block=lambda target, text, mode="tell": gameplay("say_targeted", mode, target, text))
    registry.tool("channel_say", description="Broadcast on a channel.", parameters={"channel": {"type": "string"}, "text": {"type": "string"}}, block=lambda channel, text: gameplay("say_channel", channel, text))
    registry.tool("get_item", description="Pick up an item.", parameters={"item": {"type": "string"}, "container": {"type": "string"}, "count": {"type": "integer"}}, block=lambda item, container=None, count=None: gameplay("get", item, container, count))
    registry.tool("drop_item", description="Drop, donate, or junk an item.", parameters={"item": {"type": "string"}, "mode": {"type": "string"}, "count": {"type": "integer"}}, block=lambda item, mode="drop", count=None: gameplay("drop", mode, item, count))
    registry.tool("put_item", description="Put an item in a container.", parameters={"item": {"type": "string"}, "container": {"type": "string"}, "count": {"type": "integer"}}, block=lambda item, container, count=None: gameplay("put", item, container, count))
    registry.tool("equip_item", description="Equip or remove an item.", parameters={"item": {"type": "string"}, "action": {"type": "string"}, "body_loc": {"type": "string"}}, block=lambda item, action, body_loc=None: gameplay("equip", action, item, body_loc))
    registry.tool("consume_item", description="Consume an item.", parameters={"item": {"type": "string"}, "mode": {"type": "string"}}, block=lambda item, mode="eat": gameplay("consume", mode, item))
    registry.tool("cast_spell", description="Cast a spell.", parameters={"spell": {"type": "string"}, "target": {"type": "string"}}, block=lambda spell, target=None: gameplay("cast", spell, target))
    registry.tool("use_magic_item", description="Use a magic item.", parameters={"item": {"type": "string"}, "mode": {"type": "string"}, "target_args": {"type": "string"}}, block=lambda item, mode, target_args=None: gameplay("use_magic_item", mode, item, target_args))
    registry.tool("shop", description="Interact with a shop.", parameters={"action": {"type": "string"}, "args": {"type": "string"}}, block=lambda action, args=None: gameplay("shop", action, args))
    registry.tool("practice", description="List or practice a skill.", parameters={"skill": {"type": "string"}}, block=lambda skill=None: gameplay("practice", skill))
    registry.tool("save_character", description="Save the character.", parameters={}, block=lambda: gameplay("save_char"))

    def send_raw(command: str) -> str:
        blocked = guard()
        if blocked:
            return blocked
        session.send_command(command)
        return session.read_until_quiet()

    registry.tool("send_raw", description="Send an arbitrary MUD command.", parameters={"command": {"type": "string"}}, block=send_raw)
    try:
        session.open()
        session.login(name, password)
    except SessionError as exc:
        # Match Ruby: registration remains usable and mud_connect can retry.
        print(f"[boukensha] MUD auto-connect failed: {exc}")
    return session


def _connect(session: Session, name: str, password: str) -> str:
    if session.is_open():
        return f"already connected to {session.host}:{session.port}"
    try:
        session.open()
        welcome = session.login(name, password)
        return f"connected to {session.host}:{session.port}\n{welcome}"
    except SessionError as exc:
        return f"error: {exc}"


def _disconnect(session: Session) -> str:
    if not session.is_open():
        return "already disconnected"
    session.close()
    return "disconnected"
