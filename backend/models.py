from sqlalchemy import Column, Integer, BigInteger, Boolean, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String, unique=True, nullable=False)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    buy_coffe = Column(Integer, default=0, nullable=False)


# class Order(Base):
# __tablename__ = "orders"

# id = Column(Integer, primary_key=True, autoincrement=True)
# user_id = Column(
#     Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
# )
# is_used = Column(Boolean, default=False, nullable=False)
