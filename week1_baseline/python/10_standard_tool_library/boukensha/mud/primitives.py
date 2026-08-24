from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    primitive: str
    raw: str
    verb: str
    args: dict[str, object]

    def __str__(self) -> str:
        return self.raw


class Primitives:
    DIRECTIONS = ("north", "east", "south", "west", "up", "down")
    POSITIONS = ("stand", "sit", "rest", "sleep", "wake")
    ATTACK_STYLES = ("hit", "murder", "kill")
    STRIKE_SKILLS = ("backstab", "bash", "kick", "rescue", "assist")
    LOCAL_SAY = ("say", "emote", "reply")
    TARGETED_SAY = ("tell", "whisper", "ask")
    CHANNELS = ("shout", "gossip", "auction", "grats", "holler")
    DROP_MODES = ("drop", "donate", "junk")
    EQUIP_OPS = ("wear", "wield", "grab", "hold", "remove")
    CONSUME_MODES = ("eat", "taste", "drink", "sip")
    SPELL_ITEM = ("use", "quaff", "recite")
    SHOP_OPS = ("buy", "sell", "list", "value", "offer")
    INFO_SELF = ("score", "inventory", "equipment", "gold", "exits", "time", "weather", "levels", "wimpy", "toggle", "where")

    @staticmethod
    def _enum(value: object, allowed: tuple[str, ...], name: str) -> str:
        normalized = str(value).lower()
        if normalized not in allowed:
            raise ValueError(f"invalid {name}: {value!r} (expected one of {', '.join(allowed)})")
        return normalized

    @staticmethod
    def _required(value: object, name: str) -> str:
        if value is None or not str(value).strip():
            raise ValueError(f"{name} is required")
        return str(value)

    @staticmethod
    def _cmd(primitive: str, verb: str, raw: str, **args: object) -> Command:
        return Command(primitive, raw, verb, args)

    def move(self, direction: str) -> Command:
        verb = self._enum(direction, self.DIRECTIONS, "direction")
        return self._cmd("move", verb, verb)

    def flee(self) -> Command:
        return self._cmd("flee", "flee", "flee")

    def set_position(self, position: str) -> Command:
        verb = self._enum(position, self.POSITIONS, "pos")
        return self._cmd("set_position", verb, verb)

    def track(self, target: str) -> Command:
        target = self._required(target, "victim")
        return self._cmd("track", "track", f"track {target}", victim=target)

    def attack(self, style: str, target: str) -> Command:
        verb = self._enum(style, self.ATTACK_STYLES, "style")
        target = self._required(target, "target")
        return self._cmd("attack", verb, f"{verb} {target}", target=target)

    def skill_strike(self, skill: str, target: str) -> Command:
        verb = self._enum(skill, self.STRIKE_SKILLS, "skill")
        target = self._required(target, "target")
        return self._cmd("skill_strike", verb, f"{verb} {target}", target=target)

    def say_local(self, mode: str, text: str) -> Command:
        verb = self._enum(mode, self.LOCAL_SAY, "mode")
        text = self._required(text, "text")
        return self._cmd("say_local", verb, f"{verb} {text}", text=text)

    def say_targeted(self, mode: str, target: str, text: str) -> Command:
        verb = self._enum(mode, self.TARGETED_SAY, "mode")
        target, text = self._required(target, "target"), self._required(text, "text")
        return self._cmd("say_targeted", verb, f"{verb} {target} {text}", target=target, text=text)

    def say_channel(self, channel: str, text: str) -> Command:
        verb = self._enum(channel, self.CHANNELS, "channel")
        text = self._required(text, "text")
        return self._cmd("say_channel", verb, f"{verb} {text}", text=text)

    def get(self, item: str, container: str | None = None, count: int | None = None) -> Command:
        item = self._required(item, "obj")
        parts = ["get"] + ([str(count)] if count is not None else []) + [item] + ([container] if container else [])
        return self._cmd("get", "get", " ".join(parts), obj=item, container=container, count=count)

    def drop(self, mode: str, item: str, count: int | None = None) -> Command:
        verb = self._enum(mode, self.DROP_MODES, "mode")
        item = self._required(item, "obj")
        parts = [verb] + ([str(count)] if count is not None else []) + [item]
        return self._cmd("drop", verb, " ".join(parts), obj=item, count=count)

    def put(self, item: str, container: str, count: int | None = None) -> Command:
        item, container = self._required(item, "obj"), self._required(container, "container")
        parts = ["put"] + ([str(count)] if count is not None else []) + [item, container]
        return self._cmd("put", "put", " ".join(parts), obj=item, container=container, count=count)

    def equip(self, action: str, item: str, body_loc: str | None = None) -> Command:
        verb = self._enum(action, self.EQUIP_OPS, "slot_op")
        item = self._required(item, "obj")
        raw = f"{verb} {item}" + (f" {body_loc}" if body_loc else "")
        return self._cmd("equip", verb, raw, obj=item, body_loc=body_loc)

    def consume(self, mode: str, item: str) -> Command:
        verb = self._enum(mode, self.CONSUME_MODES, "mode")
        item = self._required(item, "obj")
        return self._cmd("consume", verb, f"{verb} {item}", obj=item)

    def cast(self, spell: str, target: str | None = None) -> Command:
        spell = self._required(spell, "spell")
        raw = f"cast '{spell}'" + (f" {target}" if target else "")
        return self._cmd("cast", "cast", raw, spell=spell, target=target)

    def use_magic_item(self, mode: str, item: str, target_args: str | None = None) -> Command:
        verb = self._enum(mode, self.SPELL_ITEM, "mode")
        item = self._required(item, "item")
        raw = f"{verb} {item}" + (f" {target_args}" if target_args else "")
        return self._cmd("use_magic_item", verb, raw, item=item, target_args=target_args)

    def shop(self, action: str, args: str | None = None) -> Command:
        verb = self._enum(action, self.SHOP_OPS, "op")
        raw = verb + (f" {args}" if args else "")
        return self._cmd("shop", verb, raw, args=args)

    def practice(self, skill: str | None = None) -> Command:
        raw = "practice" + (f" {skill}" if skill else "")
        return self._cmd("practice", "practice", raw, skill=skill)

    def save_char(self) -> Command:
        return self._cmd("save_char", "save", "save")

    def look(self, target: str | None = None, preposition: str | None = None) -> Command:
        target = None if not str(target or "").strip() else target
        preposition = None if not str(preposition or "").strip() else preposition
        if preposition is not None and preposition.lower() not in ("in", "at", *self.DIRECTIONS):
            raise ValueError(f"invalid preposition: {preposition!r}")
        raw = "look" + (f" {preposition}" if preposition else "") + (f" {target}" if target else "")
        return self._cmd("look", "look", raw, target=target, preposition=preposition)

    def examine(self, target: str) -> Command:
        target = self._required(target, "target")
        return self._cmd("examine", "examine", f"examine {target}", target=target)

    def info_self(self, kind: str) -> Command:
        verb = self._enum(kind, self.INFO_SELF, "kind")
        return self._cmd("info_self", verb, verb)

    def consider(self, target: str) -> Command:
        target = self._required(target, "target")
        return self._cmd("consider", "consider", f"consider {target}", target=target)
