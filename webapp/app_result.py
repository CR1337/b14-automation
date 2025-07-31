from dataclasses import dataclass
import traceback
from typing import Any, Dict


@dataclass
class AppResult:
    stage: str
    success: bool
    exception: BaseException | None
    app_dict: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        if self.exception is None:
            return {
                "stage": self.stage,
                "success": self.success,
                "exception": None,
                "app_dict": self.app_dict,
            }
        else:
            return {
                "stage": self.stage,
                "success": self.success,
                "exception": "".join(
                    traceback.format_exception(
                        type(self.exception),
                        self.exception,
                        self.exception.__traceback__,
                    )
                ),
                "app_dict": self.app_dict,
            }
