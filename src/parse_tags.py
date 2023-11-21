import yake
from pathlib import Path

from ofdb import OFDB

from models.post_sql import Content, Tag
from sqlmodel import Session, select

from util import cleanup_text

special_tags = []


def populate_special_tags():
    global special_tags
    try:
        with open(".special_tags.txt", "r") as file_obj:
            special_tags = file_obj.read().lower().strip().split()
    except IOError:
        pass


def get_tags(text) -> list[Tag]:
    if text is None:
        return []

    text = cleanup_text(text)
    kw_extractor = yake.KeywordExtractor(n=1, dedupLim=0.1)
    keywords = [item[0].lower() for item in kw_extractor.extract_keywords(text)]
    for tag in special_tags:
        if tag in text:
            print("found special tag", tag)
            keywords.append(tag)
    return list(set(keywords))


if __name__ == "__main__":
    db = OFDB()
    populate_special_tags()
    with Session(db.engine) as session:
        statement = select(Content)
        result = session.exec(statement)
        for item in result:
            tags = get_tags(item.text)
            if tags == []:
                continue
            tag_ids = db.upsert_tags(tags)
            for tag_id in tag_ids:
                print(tag_id)
                if tag_id not in item.tags:
                    item.tags.append(tag_id)

            # item.tags = tag_ids
            # session.add(item)
            session.commit()

    # db.link_tags_to_post(tag_ids, item)
