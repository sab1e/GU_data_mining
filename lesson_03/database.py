from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Post, Writer, Tag, Hub
from habra_parser import HabraBestDayParser


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        try:
            session.commit()
            return instance
        except Exception as e:
            print(e)
            session.rollback()


if __name__ == '__main__':
    parser = HabraBestDayParser()
    parser.parse_rows()
    parser.post_page_parse()

    engine = create_engine('sqlite:///habr.db')
    Base.metadata.create_all(engine)

    session_db = sessionmaker(bind=engine)
    session = session_db()

    for post in parser.post_data:
        writer = get_or_create(session, Writer,
                               name=post.get('writer_name'),
                               url=post.get('writer_url'))
        tags = [get_or_create(session, Tag, name=tag, url=url)
                for tag, url in post.get('tags').items()]
        hubs = [get_or_create(session, Hub, name=hub, url=url)
                for hub, url in post.get('hubs').items()]
        post = get_or_create(session, Post,
                             title=post.get('title'),
                             url=post.get('url'),
                             writer_id=writer.id)

        post.tag.extend(tags)
        post.hub.extend(hubs)

        session.add(post)
        session.commit()

    session.close()
