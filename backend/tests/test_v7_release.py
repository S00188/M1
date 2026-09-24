import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.config import Settings
from app.database import _prepare_asyncpg_url
from app.game_engine.engine import GameEngine
from app.game_engine.persistence import state_from_dict, state_to_dict
from app.game_engine.roles import RoleName, Faction
from app.game_engine.state import Phase, WinResult
from app.services.game_service import GameRegistry
from app.services import notifications as n


def match():
    engine = GameEngine("v7", 1, "<Ali & Vali>", chat_id="-100")
    engine.state.players[engine.state.host_id].role = RoleName.CITIZEN
    engine.state.phase = Phase.ROLE_ASSIGNMENT
    return engine


@pytest.fixture
def sender(monkeypatch):
    send = AsyncMock(return_value=True)
    monkeypatch.setattr(n, "send_telegram_message", send)
    monkeypatch.setattr("app.services.checkpoint_service.save_checkpoint", AsyncMock())
    n.forget_game("v7")
    return send


def test_duplicate_group_blocked_until_finished():
    reg = GameRegistry()
    first = reg.create(1, "Ali", "-100")
    for phase in (Phase.LOBBY, Phase.NIGHT, Phase.VOTING):
        first.state.phase = phase
        with pytest.raises(ValueError):
            reg.create(2, "Vali", "-100")
        assert reg.get_or_create_for_chat("-100", 2, "Vali") == (first, False)
    first.state.phase = Phase.GAME_OVER
    assert reg.create(2, "Vali", "-100") is not first


@pytest.mark.asyncio
async def test_start_first_observation_private_and_concurrent(sender):
    engine = match()
    await asyncio.gather(*(n.notify_group_if_phase_changed(engine) for _ in range(5)))
    sender.assert_awaited_once()
    text = sender.call_args.args[1]
    assert "Tinch aholi — 1" in text
    assert "Ali" not in text
    restored = GameEngine.from_state(state_from_dict(state_to_dict(engine.state)))
    await n.notify_group_on_restart(restored)
    await n.notify_group_if_phase_changed(restored)
    sender.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_send_retried(sender):
    sender.side_effect = [False, True]
    engine = match()
    await n.notify_group_if_phase_changed(engine)
    assert not engine.state.group_start_announced
    n._retry_after.clear()
    await n.notify_group_if_phase_changed(engine)
    assert engine.state.group_start_announced
    assert sender.await_count == 2


@pytest.mark.asyncio
async def test_end_escaped_and_individual_winner(sender):
    engine = match()
    engine.state.phase = Phase.GAME_OVER
    engine.state.winner = WinResult(faction=Faction.TOWN, winners=[],
        individual_winners=[engine.state.host_id], reason="test")
    await n.notify_group_if_phase_changed(engine)
    await n.notify_group_if_phase_changed(engine)
    sender.assert_awaited_once()
    text = sender.call_args.args[1]
    assert "🏆 &lt;Ali &amp; Vali&gt;" in text
    assert "Tinch aholi" in text and "/start" in text


@pytest.mark.parametrize("scheme", ["postgres", "postgresql"])
def test_pasted_postgres_url(scheme):
    url, args = _prepare_asyncpg_url(f"{scheme}://user:pw@host/db?sslmode=require")
    assert url == "postgresql+asyncpg://user:pw@host/db"
    assert args["ssl"] == "require"


def test_production_rejects_defaults():
    with pytest.raises(ValueError, match="DATABASE_URL"):
        Settings(_env_file=None, environment="production").validate_deployment()


@pytest.mark.asyncio
async def test_add_admin_link(monkeypatch):
    from app import telegram_bot as bot
    monkeypatch.setattr(bot, "get_bot_username", AsyncMock(return_value="sample_bot"))
    send = AsyncMock()
    monkeypatch.setattr(bot, "_edit_or_send", send)
    await bot.on_add_group(SimpleNamespace(chat=SimpleNamespace(id=123)))
    button = send.call_args.kwargs["reply_markup"].inline_keyboard[0][0]
    assert button.url == "https://t.me/sample_bot?startgroup=mafia&admin=manage_chat"


@pytest.mark.asyncio
async def test_profile_opens_home(monkeypatch):
    from app import telegram_bot as bot
    monkeypatch.setattr(bot, "get_user_language", AsyncMock(return_value="uz"))
    monkeypatch.setattr(bot, "webapp_base_url", lambda: "https://example.test")
    send = AsyncMock()
    monkeypatch.setattr(bot, "_edit_or_send", send)
    await bot.on_profile_button(SimpleNamespace(chat=SimpleNamespace(id=123), from_user=SimpleNamespace(id=123)))
    url = send.call_args.kwargs["reply_markup"].inline_keyboard[0][0].web_app.url
    assert "?view=home&lang=uz" in url
