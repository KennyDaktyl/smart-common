from typing import Callable, Type
from pydantic import BaseModel


class WizardStep:
    def __init__(
        self,
        schema: Type[BaseModel],
        handler: Callable[[BaseModel], dict],
    ):
        self.schema = schema
        self.handler = handler
