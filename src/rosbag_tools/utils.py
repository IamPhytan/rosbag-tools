from functools import wraps
from pathlib import Path

import click
from rosbags.typesys import get_types_from_msg, register_types


def guess_msgtype(path: Path) -> str:
    """Guess message type name from path."""
    name = path.relative_to(path.parents[2]).with_suffix("")
    if "msg" not in name.parts:
        name = name.parent / "msg" / name.name
    return str(name)


def custom_message_path(f):
    @wraps(f)
    @click.option(
        "--msg",
        "--msg-path",
        "msg_path",
        type=click.Path(exists=True),
        help="Custom messages path. Can be a path to a ROS workspace.",
    )
    def wrapper(msg_path, *args, **kwargs):
        if msg_path:
            add_types = {}
            custom_path = Path(msg_path)
            all_msg_paths = tuple(custom_path.rglob("**/msg/*.msg"))
            msg_paths = tuple(p for p in all_msg_paths if "install" not in p.parts)
            for msgpath in msg_paths:
                msgdef = msgpath.read_text(encoding="utf-8")
                add_types.update(get_types_from_msg(msgdef, guess_msgtype(msgpath)))
            register_types(add_types)
        return f(*args, **kwargs)

    return wrapper
