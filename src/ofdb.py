from datetime import datetime

from loguru import logger as log
from models.post_sql import Content, Tag, ContentTagLink, Media
from models.messages import Message
from models.media import MediaItem
from models.post import Post
from models.purchase import Purchase
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.sql.expression import SelectOfScalar

ContentType = Message | Post | Purchase


class OFDB:
    db_path: str

    def __init__(self, db_path="data_ofd.db"):
        self.db_path = f"sqlite:///{db_path}"
        log.info(f"Creating database: {self.db_path}")
        self.engine = create_engine(self.db_path)
        SQLModel.metadata.create_all(self.engine)

    def _upsert(self, item, statement: SelectOfScalar):
        with Session(self.engine) as session:
            result = session.exec(statement).first()
            if result is None:
                result = item

            for key, value in item.model_dump(exclude_unset=True).items():
                setattr(result, key, value)
            session.add(result)
            session.commit()
            session.refresh(result)
            return result

    def _update(self, item):
        with Session(self.engine) as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def upsert_content(self, content: ContentType):
        profile_id = content.get_profile_id()
        if profile_id is None:
            return
        statement = select(Content).where(Content.id == content.id)  # type: ignore
        item = Content(
            id=content.id,
            profile_id=profile_id,
            date=datetime.strptime(content.get_date(), "%Y-%m-%d"),
            text=content.text,
        )
        self._upsert(item, statement)

    def upsert_tags(self, tags):
        tag_results = []
        for tag in tags:
            item = Tag(name=tag)
            statement = select(Tag).where(Tag.name == tag)
            result = self._upsert(item, statement)
            tag_results.append(result)
        return tag_results

    def link_tags_to_post(self, tags: list[Tag], content: Content):
        content.tags = tags
        self._update(content)

        # for tag in tags:
        #     if tag is None:
        #         continue
        #     item = ContentTagLink(tag_id=tag, content_id=content.id)
        #     statement = select(ContentTagLink).where(
        #         ContentTagLink.tag_id == tag and ContentTagLink.content_id == content.id  # type: ignore
        #     )
        #     self._upsert(item, statement)

    def upsert_media_item(
        self, file_path: str, profile_id: int, media: MediaItem, mediaType: str, postdate: str, album="", post_id=0
    ):
        item = Media(
            file_path=file_path,
            profile_id=profile_id,
            id=media.id,
            content_id=post_id,
            media_type=mediaType,
            postdate=datetime.strptime(postdate, "%Y-%m-%d"),
        )
        statement = select(Media).where(Media.id == media.id)  # type: ignore
        self._upsert(item, statement)
