import yake
from ofdb import OFDB

from models.post_sql import Content, Tag
from sqlmodel import Session, select

from util import cleanup_text

special_tags = []


def load_special_tags():
    global special_tags
    try:
        with open(".special_tags.txt", "r") as file_obj:
            special_tags = set(file_obj.read().lower().strip().split())
    except IOError:
        pass


def get_special_tags(text):
    keywords = []
    global special_tags
    for tag in special_tags:
        if tag in text:
            keywords.append(tag)
    return keywords


def get_tags(text) -> list[Tag]:
    if text is None:
        return []

    text = cleanup_text(text)
    kw_extractor = yake.KeywordExtractor(n=1, dedupLim=0.1)
    keywords = [item[0].lower() for item in kw_extractor.extract_keywords(text)]
    keywords += get_special_tags(text)
    return list(set(keywords))


if __name__ == "__main__":
    db = OFDB()
    load_special_tags()
    with Session(db.engine) as session:
        statement = select(Content)  # .where(Content.id == 3118351114)
        result = session.exec(statement)
        for item in result:
            tags = get_special_tags(item.text.lower())
            tag_ids = db.upsert_tags(tags)
            existing_tag_ids = [x.id for x in item.tags]
            for tag_id in [tag_id for tag_id in tag_ids if tag_id.id not in existing_tag_ids]:
                item.tags.append(tag_id)
            session.commit()

    # db.link_tags_to_post(tag_ids, item)
