from pydantic import BaseModel


class DynamicRule(BaseModel):
    static_param: str
    format: str
    checksum_indexes: list[int]
    checksum_constants: list[int] | None = None
    checksum_constant: int
    app_token: str
    remove_headers: list[str] | None = None
    error_code: int | None = None
    message: str | None = None
