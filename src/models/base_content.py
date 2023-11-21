from pydantic import BaseModel


class BaseContent(BaseModel):
    def get_date(self):
        raise NotImplementedError

    def get_profile_id(self):
        raise NotImplementedError
