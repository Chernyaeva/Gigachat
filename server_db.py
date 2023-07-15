import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime


class ServerStorage:
    '''
    Declares server database and methods to work with it.
    Uses SQLite and SQLAlchemy ORM.
    '''

    # Create base class for declarative work
    Base = declarative_base()

    class User(Base):
        '''Table to store usernames and passwords'''
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        password = Column(String, unique=False)

        def __init__(self, name, password):
            self.name = name
            self.password = password

        def __repr__(self):
            return f'User #{self.id}: {self.name}'

    class UsersHystory(Base):
        '''Table to store user's login history'''
        __tablename__ = 'users_hystiry'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        login_time = Column(DateTime)

        def __init__(self, user_id, login_time):
            self.user_id = user_id
            self.login_time = login_time

        def __repr__(self):
            return f'User #{self.user_id} logged in at {self.login_time }'

    class MessageHistory(Base):
        '''Table to store user's message history'''
        __tablename__ = 'message_history'
        id = Column(Integer, primary_key=True)
        sender_id = Column(Integer, ForeignKey('users.id'))
        receiver_id = Column(Integer, ForeignKey('users.id'))
        message = Column(String)

        def __init__(self, sender_id, receiver_id, message):
            self.sender_id = sender_id
            self.receiver_id = receiver_id
            self.message = message

        def __repr__(self):
            return f'Message #{self.id}. User {self.sender_id} wrote to {self.receiver_id } {self.message}'

    class Contacts(Base):
        '''Table to store user's contacts'''
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        contact_id = Column(Integer, ForeignKey('users.id'))
        contact_name = Column(String)

        def __init__(self, user_id, contact_id, contact_name):
            self.user_id = user_id
            self.contact_id = contact_id
            self.contact_name = contact_name

        def __repr__(self):
            return f'User #{self.user_id} is friend with #{self.contact_id} {self.contact_name}'

    def __init__(self):
        self.engine = create_engine(
            'sqlite:///server_base.db3',
            echo=False,
            pool_recycle=7200)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Create tables
        self.Base.metadata.create_all(self.engine)

    def user_login(self, username, password):
        '''Adds new user to Users table and adds login event to UsersHystory table'''
        # Запрос в таблицу пользователей на наличие там пользователя с таким
        # именем
        rez = self.session.query(self.User).filter_by(name=username)
        # Если имя пользователя уже присутствует в таблице, обновляем время
        # последнего входа
        if not rez.count():
            # Создаем экземпляр класса self.Users, через который передаем
            # данные в таблицу
            user = self.User(username, password)
            self.session.add(user)
            # Комит здесь нужен, чтобы присвоился ID
            self.session.commit()
            user_id = self.session.query(
                self.User).filter_by(
                name=username).first().id
        else:
            user_id = rez.first().id
            # Check user password
            if rez.first().password != password:
                return -1  # wrong password
        new_user_login = self.UsersHystory(user_id, datetime.datetime.now())
        self.session.add(new_user_login)
        # Сохраняем изменения
        self.session.commit()
        return 0

    def save_message(self, sendername, receivername, message):
        '''Saves message to MessageHistory table'''
        # Query users IDs from users table
        senderid = self.session.query(
            self.User).filter_by(
            name=sendername).first().id
        receiver = self.session.query(self.User).filter_by(name=receivername)
        if receiver.count():
            receiverid = receiver.first().id
            new_message = self.MessageHistory(senderid, receiverid, message)
            self.session.add(new_message)
            self.session.commit()

    def add_contact(self, user_name, contact_name):
        '''Saves new contact for user to Contacts table'''
        # Query users IDs from users table
        user_id = self.session.query(
            self.User).filter_by(
            name=user_name).first().id
        contact = self.session.query(self.User).filter_by(name=contact_name)
        if contact.count():
            contact_id = contact.first().id
            if not self.session.query(
                    self.Contacts).filter_by(
                    user_id=user_id,
                    contact_id=contact_id).count():
                new_contact = self.Contacts(user_id, contact_id, contact_name)
                self.session.add(new_contact)
                self.session.commit()

    def get_contacts(self, user_name):
        '''Returns list of contacts for user'''
        user_id = self.session.query(
            self.User).filter_by(
            name=user_name).first().id
        contacts = self.session.query(
            self.Contacts).filter_by(
            user_id=user_id).all()
        contacts_list = []
        for contact in contacts:
            contacts_list.append(contact.contact_name)
        return contacts_list

    def get_users(self):
        '''Returns all user from User table'''
        users = self.session.query(self.User).all()
        users_list = []
        for user in users:
            users_list.append(user.name)
        return users_list

    def get_users_history(self):
        '''Returns all entries from UsersHystory table'''
        users = self.session.query(self.UsersHystory).all()
        users_list = []
        for user in users:
            users_list.append(
                f'User#{user.user_id} logged in at {user.login_time}')
        return users_list


if __name__ == '__main__':
    storage = ServerStorage()
    # admin_user = storage.User("vasia",)
    # storage.session.add(admin_user)
    # other_user = storage.User("petia",)
    # storage.session.add(other_user)
    storage.user_login('vasia')
    storage.user_login('petia')
    storage.user_login('igor')
    q_user1 = storage.session.query(
        storage.User).filter_by(
        name="vasia").first()
    q_user2 = storage.session.query(
        storage.User).filter_by(
        name="petia").first()
    print('Simple query1:', q_user1)
    print('Simple query2:', q_user2)
    storage.save_message('vasia', 'petia', 'Hello!')
    message = storage.session.query(storage.MessageHistory).first()
    print(message)
    storage.add_contact("vasia", 'petia')
    storage.add_contact("vasia", 'igor')
    print(storage.get_contacts("vasia"))
