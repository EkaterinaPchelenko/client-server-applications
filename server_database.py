import datetime

import sqlalchemy
from sqlalchemy import create_engine, Integer, String, DateTime, ForeignKey, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy.testing.schema import Column
from common.variables import *


class ServerStorage:

    class AllUsers:
        def __init__(self, name):
            self.name = name
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveUsers:
        def __init__(self, user, ip_address, port, login_time):
            self.user = user
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        def __init__(self, name, date_time, ip, port):
            self.id = None
            self.name = name
            self.date_time = date_time
            self.ip = ip
            self.port = port

    def __init__(self):
        self.engine = create_engine('sqlite:///server_base.db3', echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        users = Table('Users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String, unique=True),
                      Column('last_login', DateTime)
                      )
        active_users = ('Active_users', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('user', ForeignKey('Users.id'), unique=True),
                        Column('ip_address', String),
                        Column('port', Integer),
                        Column('login_time', DateTime))
        users_history = ('Users_history', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name',  ForeignKey('Users.id')),
                         Column('date_time', DateTime),
                         Column('ip', String),
                         Column('port', String))

        self.metadata.create_all(self.engine)
        mapper(self.AllUsers, users)
        mapper(self.ActiveUsers, active_users)
        mapper(self.LoginHistory, users_history)

        session = sessionmaker(bind=self.engine)
        self.session = session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        res = self.session.query(self.AllUsers).filter_by(name=username)

        if res.count():
            user = res.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(active_user)

        hist = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(hist)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).first()

        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()

        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
        )

        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time,
        ).join(self.AllUsers)

        return query.all()

    def loging_history(self, username=None):
        query = self.session.query(
            self.AllUsers.name,
            self.LoginHistory.date_time,
            self.LoginHistory.ip,
            self.LoginHistory.port
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()


if __name__ == '__main__':
    test = ServerStorage()
    test.user_login('test1', '192.168.1.6', 6666)
    test.user_login('test2', '192.168.1.7', 7777)

    print(test.active_users_list())

    test.user_logout('test1')
    print(test.active_users_list())

    test.loging_history('test1')
    print(test.users_list())
