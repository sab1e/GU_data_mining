from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Post, Writer, Tag, Hub
from habra_parser import HabraBestDayParser

if __name__ == '__main__':
    parser = HabraBestDayParser()
    parser.parse_rows()
    parser.post_page_parse()

    engine = create_engine('sqlite:///habr.db')
    Base.metadata.create_all(engine)

    session_db = sessionmaker(bind=engine)
    session = session_db()

    for post in parser.post_data:
        writer = Writer(post.get('writer_name'),
                        post.get('writer_url'))
        tags = [Tag(f'{tag}', f'{url}') for tag, url in post.get('tags').items()]
        hubs = [Hub(f'{hub}', f'{url}') for hub, url in post.get('hubs').items()]
        post = Post(post.get('title'), post.get('url'), writer.id)
        print(writer.name)
        session.add(writer)
        session.add(post)

    try:
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()
