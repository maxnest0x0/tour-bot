from abc import ABC, abstractmethod
from typing import Awaitable, Any, Sequence, cast

from bot.data_types import ParamsState, ParamsStateUpdate, InputParam

Params = tuple[InputParam, InputParam]

class Parser(ABC):
    @abstractmethod
    def parse(self, text: str, state: ParamsState) -> ParamsState | Awaitable[ParamsState]:
        pass

    def _decide_without_preposition(self, res: ParamsStateUpdate, state: ParamsState, values: Sequence[Any], params_in_order: Params, params_by_priority: Params) -> ParamsStateUpdate:
        res = res.copy()

        if len(values) == 2:
            value1, value2 = values
            param1, param2 = params_in_order

            res[param1] = value1
            res[param2] = value2

        if len(values) == 1:
            value = values[0]
            param1, param2 = params_by_priority

            if res[param2] is not None:
                res[param1] = value
            elif res[param1] is not None:
                res[param2] = value
            elif state[param2] is not None:
                res[param1] = value
            elif state[param1] is not None:
                res[param2] = value
            else:
                res[param1] = value

        return res

    def _update_state(self, res: ParamsStateUpdate, state: ParamsState) -> ParamsState:
        update = cast(ParamsStateUpdate, {key: value for key, value in res.items() if value is not None})

        new_state = state.copy()
        new_state.update(update)

        return new_state
