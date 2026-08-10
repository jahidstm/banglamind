"""
BanglaMind — SQLAlchemy Database Models
=========================================
তিনটি টেবিল:
- Business : প্রতিটি ক্লায়েন্ট ব্যবসার তথ্য
- Message  : চ্যাট মেসেজের ইতিহাস
- FAQ      : প্রতিটি ব্যবসার FAQ
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer,
    Float, DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Business(Base):
    """
    একটি ব্যবসার সব তথ্য।
    প্রতিটি ব্যবসার একটি unique api_key থাকে।
    """
    __tablename__ = "businesses"

    id            = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name          = Column(String(200), nullable=False, index=True)
    phone         = Column(String(30),  nullable=True)
    address       = Column(Text,        nullable=True)
    hours         = Column(String(200), nullable=True)
    delivery_info = Column(Text,        nullable=True)
    email         = Column(String(200), nullable=True)
    facebook      = Column(String(300), nullable=True)
    whatsapp      = Column(String(50),  nullable=True)
    api_key       = Column(String(64),  unique=True, nullable=False, index=True,
                           default=lambda: uuid.uuid4().hex)
    is_active     = Column(Boolean,     default=True)
    created_at    = Column(DateTime,    default=datetime.utcnow)
    updated_at    = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    messages = relationship("Message", back_populates="business", cascade="all, delete-orphan")
    faqs     = relationship("FAQ",     back_populates="business", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Business name={self.name!r}>"


class Message(Base):
    """
    প্রতিটি চ্যাট মেসেজ এখানে সেভ হয়।
    Analytics এবং ইতিহাস দেখার জন্য।
    """
    __tablename__ = "messages"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    business_id   = Column(String(36), ForeignKey("businesses.id"), nullable=True, index=True)
    user_message  = Column(Text,    nullable=False)
    bot_reply     = Column(Text,    nullable=False)
    intent_tag    = Column(String(50),  nullable=True)
    intent_source = Column(String(10),  nullable=True)   # ml / rule / rag
    confidence    = Column(String(10),  nullable=True)   # high / medium / low
    score         = Column(Float,       nullable=True)
    language      = Column(String(20),  nullable=True)   # bengali / banglish / english
    created_at    = Column(DateTime,    default=datetime.utcnow, index=True)

    # Relations
    business = relationship("Business", back_populates="messages")

    def __repr__(self):
        return f"<Message intent={self.intent_tag!r}>"


class FAQ(Base):
    """
    প্রতিটি ব্যবসার জন্য আলাদা FAQ।
    RAG Engine এই টেবিল থেকে ডাটা নেবে।
    """
    __tablename__ = "faqs"

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=True, index=True)
    question    = Column(Text,       nullable=False)
    answer      = Column(Text,       nullable=False)
    tags        = Column(Text,       nullable=True)   # comma-separated
    is_active   = Column(Boolean,    default=True)
    created_at  = Column(DateTime,   default=datetime.utcnow)

    # Relations
    business = relationship("Business", back_populates="faqs")

    def __repr__(self):
        return f"<FAQ question={self.question[:40]!r}>"
