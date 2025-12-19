# smart_common/providers/provider_config/huawei/auth.py
from pydantic import Field
from smart_common.schemas.base import APIModel


class HuaweiAuthStep(APIModel):
    username: str = Field(..., description="Huawei FusionSolar username")
    password: str = Field(..., description="Huawei FusionSolar password")
