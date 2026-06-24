"""Tests for the bot-admin commands in bot.py (load / unload / reload).

These call the command callbacks directly (bypassing the manage_guild
permission check) with the global bot's extension loaders patched.
"""
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest

import bot as botmod


@pytest.fixture
def ctx():
    c = MagicMock()
    c.send = AsyncMock()
    return c


async def test_load_success(ctx, monkeypatch):
    monkeypatch.setattr(botmod.bot, "load_extension", AsyncMock())
    await botmod.load.callback(ctx, "dice")
    ctx.send.assert_awaited_with("dice loaded.")


async def test_load_already_loaded(ctx, monkeypatch):
    exc = discord.ext.commands.ExtensionAlreadyLoaded("cogs.dice")
    monkeypatch.setattr(
        botmod.bot,
        "load_extension",
        AsyncMock(
            side_effect=exc))
    await botmod.load.callback(ctx, "dice")
    assert "already loaded" in ctx.send.call_args.args[0]


async def test_unload_success(ctx, monkeypatch):
    monkeypatch.setattr(botmod.bot, "unload_extension", AsyncMock())
    await botmod.unload.callback(ctx, "dice")
    ctx.send.assert_awaited_with("dice unloaded.")


async def test_unload_not_loaded(ctx, monkeypatch):
    exc = discord.ext.commands.ExtensionNotLoaded("cogs.dice")
    monkeypatch.setattr(
        botmod.bot,
        "unload_extension",
        AsyncMock(
            side_effect=exc))
    await botmod.unload.callback(ctx, "dice")
    assert "not loaded" in ctx.send.call_args.args[0]


async def test_reload_unloads_then_loads(ctx, monkeypatch):
    unload = AsyncMock()
    load = AsyncMock()
    monkeypatch.setattr(botmod.bot, "unload_extension", unload)
    monkeypatch.setattr(botmod.bot, "load_extension", load)
    await botmod.reload.callback(ctx, "dice")
    unload.assert_awaited()
    load.assert_awaited()
