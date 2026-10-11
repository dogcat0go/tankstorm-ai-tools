# tankstorm-keepalive  Copyright (C) 2026 Dimlitter
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# 本程序是自由软件：你可以依据自由软件基金会发布的 GNU Affero 通用公共许可证
# （第 3 版，或你选择的任何更新版本）之条款，再分发和/或修改它。
# 本程序希望能有用，但不提供任何担保；甚至不含适销性或特定用途适用性的默示担保。
# 详见随附的 LICENSE 文件，或 <https://www.gnu.org/licenses/>。
"""坦克风暴（QQ空间 appid 100616028）每日任务脚本 —— 纯 HTTP 请求实现。"""

APPID = "100616028"
HALL_APPID = "10407"
GAME_URL = f"https://game.qzone.qq.com/{APPID}?via={APPID}_QZSTORE.V6.MY-APPS&"
HALL_GAME_URL = (
    f"https://minigame.qq.com/plat/social_hall/app_frame/?appid={HALL_APPID}")

PLAT_QZONE = "空间"
PLAT_HALL = "大厅"
PLATFORM_COOKIE = "ts_login_platform"

_HALL_ALIASES = {
    PLAT_HALL, "大厅", "qqgame", "hall", "游戏大厅", "QQ游戏大厅", "qq游戏大厅",
}
_QZONE_ALIASES = {
    PLAT_QZONE, "空间", "qzone", "QQ空间", "qq空间", "",
}


def normalize_platform(name) -> str:
    text = str(name or "").strip()
    if text in _HALL_ALIASES:
        return PLAT_HALL
    if text in _QZONE_ALIASES:
        return PLAT_QZONE
    lowered = text.lower()
    if lowered in _HALL_ALIASES or "大厅" in text:
        return PLAT_HALL
    if lowered in _QZONE_ALIASES or "空间" in text:
        return PLAT_QZONE
    return PLAT_QZONE


def platform_spec(name) -> dict:
    plat = normalize_platform(name)
    if plat == PLAT_HALL:
        return {
            "name": PLAT_HALL,
            "kind": "hall",
            "ptlogin_appid": "7000201",
            "daid": "207",
            "game_url": HALL_GAME_URL,
            "proxy_url": ("https://minigame.qq.com/plat/social_hall/"
                          "app_frame/ptlogin_proxy.html"),
            "p_skey_needles": ("minigame", "qqgame"),
            "napcat_domain": "minigame.qq.com",
            "p_skey_domain": ".minigame.qq.com",
            "hall_appid": HALL_APPID,
        }
    return {
        "name": PLAT_QZONE,
        "kind": "qzone",
        "ptlogin_appid": "549000912",
        "daid": "5",
        "game_url": GAME_URL,
        "proxy_url": "https://qzs.qq.com/qzone/v6/portal/proxy.html",
        "p_skey_needles": ("qzone",),
        "napcat_domain": "game.qzone.qq.com",
        "p_skey_domain": ".qzone.qq.com",
        "hall_appid": "",
    }


def config_platform(config: dict | None) -> str:
    login = (config or {}).get("登录") or {}
    return normalize_platform(login.get("平台"))
