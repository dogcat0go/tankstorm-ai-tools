# tankstorm-keepalive  Copyright (C) 2026 Dimlitter
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# 本程序是自由软件：你可以依据自由软件基金会发布的 GNU Affero 通用公共许可证
# （第 3 版，或你选择的任何更新版本）之条款，再分发和/或修改它。
# 本程序希望能有用，但不提供任何担保；甚至不含适销性或特定用途适用性的默示担保。
# 详见随附的 LICENSE 文件，或 <https://www.gnu.org/licenses/>。
"""基地里用工程师把残血坦克修满。

2026-10-11 19:44 抓包：5 个工程师（type=8）先修猛犸（30582，type=45），
再修 T99（30433，type=90）。客户端只上报被修的坦克，不报工程师。

登录的 RseLoadArmy 里 type 不是兵种号，要按客户端 checkarmyType 还原：

    t = (((type - stance*20) + Y*200) - X*100) / health
    c = (((check + stance*30) - health*12) + Y) - X
    t == c 时 t 才是兵种号，否则当无效单位丢掉。

坐标只在本地算。寻路不做：坦克离所有工程师都超过射程时，把上报坐标
放到工程师中间。工程师射程是表里的 attackRange=50。治疗量按这次抓包
的稳态：满级工程师每发 440，弹夹 1、装填 20 帧、逻辑 30 帧/秒，
每人每秒 660，五个人约 3300/秒，和 12 秒一包、每包大约 +39600 对得上。
"""

from __future__ import annotations

import math
import time

from . import sender
from .log import get_logger
from .proto_encode import encode_bytes, encode_int32, encode_message

log = get_logger()

# 表里治疗类型 heal=2。heal=1 是医疗兵，不修坦克。
ENGINEERS = frozenset({8, 50})
# 第 2 张兵种表里 group=2 的全部 type。
TANKS = frozenset({
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 31, 32, 34, 35, 36, 37,
    39, 40, 41, 42, 45, 46, 47, 48, 49, 51, 52, 54, 55, 56, 57, 58, 59, 61,
    62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
    85, 86, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102,
    103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
})
NAMES = {
    8: "工程师", 50: "不死工程师",
    12: "防空车",
    45: "猛犸坦克", 49: "黄金猛犸坦克",
    90: "T99主战坦克", 91: "黄金T99",
}

REPAIR_RANGE = 50
HEAL_PER_SEC = 660
SYNC_SEC = 12
BUDGET_SEC = 180
OPCODE = "0427"


def _s32(n) -> int:
    n = int(n) & 0xFFFFFFFF
    if n >= 0x80000000:
        return n - 0x100000000
    return n


def real_type(raw_type, x, y, health, stance, check):
    """还原兵种号。校验不过返回 None。"""
    t = _s32(raw_type)
    t = _s32(t - _s32(stance) * 20)
    t = _s32(t + _s32(y) * 200)
    t = _s32(t - _s32(x) * 100)
    h = _s32(health)
    if h == 0:
        return None
    t = int(t / h)
    c = _s32(check)
    c = _s32(c + _s32(stance) * 30)
    c = _s32(c - h * 12)
    c = _s32(c + _s32(y))
    c = _s32(c - _s32(x))
    if t != c:
        return None
    return t


def _rows(data):
    if not isinstance(data, dict):
        return []
    army = data.get("army")
    if isinstance(army, dict):
        return [army]
    if isinstance(army, list):
        return [a for a in army if isinstance(a, dict)]
    return []


def _loaded(rec):
    """登录推来的 RseLoadArmy。多段时拼到 end 为止。"""
    hist = []
    if rec is not None:
        hist = list(getattr(rec, "recent", {}).get("RseLoadArmy") or [])
        if not hist:
            one = (getattr(rec, "latest", {}) or {}).get("RseLoadArmy")
            if one:
                hist = [one]
    buf = []
    done = []
    for item in hist:
        data = item[1] if isinstance(item, tuple) else item
        buf.extend(_rows(data))
        if isinstance(data, dict) and data.get("end"):
            done = buf
            buf = []
    return done or buf


def blast_ids(rec):
    """登录兵册里还活着的爆破兵。兵种号是 7，和制造配方一样，包里的 type 要先还原。
    还没收到兵册时返回 None。"""
    if rec is None:
        return None
    hist = list(getattr(rec, "recent", {}).get("RseLoadArmy") or [])
    if not hist and not (getattr(rec, "latest", {}) or {}).get("RseLoadArmy"):
        return None
    ids = set()
    for row in _loaded(rec):
        unit = _unit(row)
        if unit and unit["type"] == 7 and unit["id"] > 0:
            ids.add(unit["id"])
    return ids


def _unit(row):
    def num(key):
        v = row.get(key)
        if isinstance(v, bool) or v is None:
            return 0
        if isinstance(v, int):
            return v
        return 0

    hp = _s32(num("field7"))
    if hp <= 0:
        return None
    typ = real_type(num("field3"), num("field4"), num("field5"),
                    num("field7"), num("field8"), num("field10"))
    if typ is None:
        return None
    return {
        "id": _s32(num("field2")),
        "type": typ,
        "x": _s32(num("field4")),
        "y": _s32(num("field5")),
        "angle": _s32(num("field6")),
        "hp": hp,
        "max": _s32(num("field16")),
        "stance": _s32(num("field8")),
    }


def _near(engs, x, y):
    return [e for e in engs
            if math.hypot(e["x"] - x, e["y"] - y) <= REPAIR_RANGE]


def _pack(tank) -> bytes:
    army = encode_message({
        2: ("int32", tank["id"]),
        3: ("int32", tank["type"]),
        4: ("int32", tank["x"]),
        5: ("int32", tank["y"]),
        6: ("int32", tank["angle"]),
        7: ("int32", tank["hp"]),
        8: ("int32", tank["stance"]),
    }, omit_zero=False)
    return encode_int32(1, 0) + encode_bytes(2, army)


def _send(rec, sock, tank):
    from . import daily
    mark = rec.seq_mark() if rec else 0
    sender.send_frame(sock, OPCODE, _pack(tank), rec.rc4_c2s if rec else None)
    data = daily._await_response(sock, rec, "RseBaseBattleModify", mark, 6.0)
    if not isinstance(data, dict):
        return False, "未收到修复回包"
    err = data.get("error")
    if err not in (0, None, False):
        return False, f"修复被拒 error={err}"
    return True, ""


def repair_tanks(rec, sock, config=None):
    """把残血坦克修到满。返回 (是否成功, 说明)。"""
    from . import daily

    units = []
    for row in _loaded(rec):
        one = _unit(row)
        if one:
            units.append(one)
    engs = [u for u in units if u["type"] in ENGINEERS]
    if not engs:
        return True, "没有工程师，跳过"
    tanks = [u for u in units
             if u["type"] in TANKS and u["max"] > u["hp"]]
    if not tanks:
        return True, f"{len(engs)} 个工程师，坦克都是满血"
    tanks.sort(key=lambda u: u["hp"] / u["max"] if u["max"] else 1)
    deadline = time.time() + BUDGET_SEC
    notes = []
    for tank in tanks:
        daily.raise_if_stopped()
        if time.time() >= deadline:
            notes.append(f"{NAMES.get(tank['type'], '坦克'+str(tank['type']))} 这轮没排上")
            break
        name = NAMES.get(tank["type"], f"坦克{tank['type']}")
        start = tank["hp"]
        if not _near(engs, tank["x"], tank["y"]):
            nearest = min(engs, key=lambda e: math.hypot(
                e["x"] - tank["x"], e["y"] - tank["y"]))
            tank["x"], tank["y"] = nearest["x"], nearest["y"]
        crew = _near(engs, tank["x"], tank["y"])
        if not crew:
            notes.append(f"{name} 旁边没有工程师")
            continue
        step = HEAL_PER_SEC * len(crew) * SYNC_SEC
        while tank["hp"] < tank["max"]:
            if time.time() + SYNC_SEC > deadline:
                break
            daily.raise_if_stopped()
            daily._nap(SYNC_SEC)
            tank["hp"] = min(tank["max"], tank["hp"] + step)
            ok, why = _send(rec, sock, tank)
            if not ok:
                return False, f"{name} {why}"
        notes.append(f"{name} {start}→{tank['hp']}"
                     + ("" if tank["hp"] >= tank["max"] else " 未满"))
    return True, f"{len(engs)} 个工程师，" + "，".join(notes)
