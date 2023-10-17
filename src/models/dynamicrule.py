from pydantic import BaseModel


class DynamicRule(BaseModel):
    static_param: str
    format: str
    checksum_indexes: list[int]
    checksum_constants: list[int]
    checksum_constant: int
    app_token: str
    remove_headers: list[str]
    error_code: int
    message: str
