from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, create_engine, ForeignKey, DateTime
import datetime

class ServerStorage:
    # Функция declarative_base создаёт базовый класс для декларативной работы
    Base = declarative_base()
    # На основании базового класса можно создавать необходимые классы
    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return f'User #{self.id}: {self.name}'
    
    class UsersHystory(Base):
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
        __tablename__ = 'message_hystory'
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
        
    def __init__(self):
        self.engine = create_engine('sqlite:///:memory:', echo=False, pool_recycle=7200)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        # Создаём таблицы
        self.Base.metadata.create_all(self.engine)


        # Функция выполняющяяся при входе пользователя, записывает в базу факт входа
    def user_login(self, username):
        # Запрос в таблицу пользователей на наличие там пользователя с таким именем
        rez = self.session.query(self.User).filter_by(name=username)
        # Если имя пользователя уже присутствует в таблице, обновляем время последнего входа
        if not rez.count():
            # Создаем экземпляр класса self.Users, через который передаем данные в таблицу
            user = self.User(username)
            self.session.add(user)
            # Комит здесь нужен, чтобы присвоился ID
            self.session.commit()
            user_id = self.session.query(self.User).filter_by(name=username).first().id
        else:
            user_id = rez.first().id    
        new_user_login = self.UsersHystory(user_id, datetime.datetime.now())     
        self.session.add(new_user_login)   
        # Сохраняем изменения
        self.session.commit()

    def save_message(self, sendername, receivername, message):
        # Query users IDs from users table
        senderid = self.session.query(self.User).filter_by(name=sendername).first().id
        receiver = self.session.query(self.User).filter_by(name=receivername)
        if receiver.count():
            receiverid = receiver.first().id 
            new_message = self.MessageHistory(senderid, receiverid, message)
            self.session.add(new_message)
            self.session.commit()

if __name__ == '__main__':

    storage = ServerStorage()
    #admin_user = storage.User("vasia",)
    #storage.session.add(admin_user)
    #other_user = storage.User("petia",)
    #storage.session.add(other_user)
    storage.user_login('vasia')
    storage.user_login('petia')
    q_user1 = storage.session.query(storage.User).filter_by(name="vasia").first()
    q_user2 = storage.session.query(storage.User).filter_by(name="petia").first()
    print('Simple query1:', q_user1)
    print('Simple query2:', q_user2)
    storage.save_message('vasia','petia','Hello!')
    message = storage.session.query(storage.MessageHistory).first()
    print(message)
