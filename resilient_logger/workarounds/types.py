from collections.abc import Callable
from typing import Any, TypeAlias

ObjectReprFn: TypeAlias = Callable[[Any], str]
