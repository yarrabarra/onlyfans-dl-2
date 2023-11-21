from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class Profile(SQLModel, table=True):  # type: ignore
    id: int = Field(primary_key=True)
    name: str


class ContentTagLink(SQLModel, table=True):  # type: ignore
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    content_id: int = Field(foreign_key="content.id", primary_key=True)


class Tag(SQLModel, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    name: str
    content: list["Content"] = Relationship(back_populates="tags", link_model=ContentTagLink)


class Media(SQLModel, table=True):  # type: ignore
    id: int = Field(primary_key=True)
    profile_id: int = Field(foreign_key="profile.id")
    content_id: int = Field(foreign_key="content.id")
    file_path: str
    media_type: str
    postdate: datetime


class Content(SQLModel, table=True):  # type: ignore
    id: int = Field(primary_key=True)
    profile_id: int = Field(foreign_key="profile.id")
    date: datetime | None
    text: str
    tags: list["Tag"] = Relationship(back_populates="content", link_model=ContentTagLink)

    def get_date(self):
        if self.date is None:
            return "1970-01-01"  # Epoch failsafe if date is not present
        return self.date.strftime("%Y-%m-%d")
