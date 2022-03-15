import re
import sys
from logzero import logger
from typing import List
from plumbum import NOHUP

try:
    from plumbum.cmd import xrandr, polybar, killall
except ImportError as e:
    logger.error(
        """
%s
It probably means the command is not installed on your system!
    """ % e.msg
    )
    sys.exit(1)

MONITORS = {"DP-0": ["left"], "DP-2": ["right"], "eDP-1-1": ["top", "bottom"]}

# FIXME put this path in the root polybar directory
POLYBAR_CONFIG = "~/.config/polybar/hack/config.ini"


def get_connected_screens() -> List[str]:
    query = xrandr["--query"]()
    return re.findall("\n(.*) connected", query)


def polybar_reload(monitor: str, position: str) -> None:
    logger.info(f"setting polybar '{position}' for '{monitor}'")
    (
        polybar.with_env(MONITOR=monitor)[
            "--reload", position, f"--config={POLYBAR_CONFIG}"
        ]
        & NOHUP(stdout="/dev/null")
    )


def set_polybar(monitor: str) -> None:
    if monitor not in MONITORS.keys():
        logger.warning(f"Unknown monitor [monitor]")
        return

    positions = MONITORS[monitor]
    for position in positions:
        polybar_reload(monitor, position)


def main() -> None:
    killall["-9", "polybar"]()
    connected = get_connected_screens()
    for screen in connected:
        set_polybar(screen)
