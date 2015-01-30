from app import db

from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.Integer)
    url = db.Column(db.String())
    result_all = db.Column(JSON)
    result_url = db.Column(db.String())

    def __init__(self, url, result_all):
        self.url = url
        self.result_all = result_all

    def __repr__(self):
        return '<id {}>'.format(self.id)


class QuerySource(db.Model):
    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(UUID(as_uuid=True))
    query_text = db.Column(db.String())

    def __init__(self, query_text):
        self.slug = self.generate_slug()
        self.query_text = query_text

    def generate_slug(self):
        return uuid.uuid4()

    def __repr__(self):
        return '<slug {}>'.format(self.slug)

