#!/usr/bin/env python3
"""Regression checks for display-name handling.

The edge Telegram console must show NODE_ALIAS/custom name when configured,
not the hostname-derived NODE_NAME. NODE_NAME remains allowed as an internal
stable identifier (registration payload / callback routing / DB key).
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TG_DAEMON = (ROOT / "core" / "tg_daemon.sh").read_text(encoding="utf-8")
TG_REPORT = (ROOT / "core" / "tg_report.sh").read_text(encoding="utf-8")
MASTER = (ROOT / "master" / "tg_master.sh").read_text(encoding="utf-8")


def test_tg_daemon_loads_display_name_from_alias():
    assert "DISPLAY_NAME" in TG_DAEMON
    assert 'DISPLAY_NAME="${NODE_ALIAS:-$NODE_NAME}"' in TG_DAEMON


def test_tg_daemon_user_facing_messages_use_display_name():
    user_facing = re.findall(r'send_msg "[^"]*|HELP_MSG="[^"]*', TG_DAEMON)
    offenders = [line for line in user_facing if "${NODE_NAME}" in line]
    assert not offenders, "user-facing tg_daemon messages still expose NODE_NAME: " + repr(offenders)
    assert "${DISPLAY_NAME}" in TG_DAEMON


def test_report_uses_alias_for_node_name():
    assert 'NODE_ALIAS="${NODE_ALIAS:-$NODE_NAME}"' in TG_REPORT
    assert "节点名称**: \\`${NODE_ALIAS}\\`" in TG_REPORT


def test_master_manage_panel_uses_alias_but_keeps_internal_id_visible():
    assert 'TARGET_ALIAS=$(db_exec "SELECT IFNULL(node_alias, node_name)' in MASTER
    assert "目标锁定**: \\`$TARGET_ALIAS\\`" in MASTER
    # The internal id may still be shown explicitly as 底层标识 for routing/debugging.
    assert "底层标识: \\`$TARGET_NODE\\`" in MASTER
