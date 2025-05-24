from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Task(Base):
  __tablename__ = "task"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True)
  description = Column(String, index=False)
  parent_id = Column(Integer, ForeignKey('task.id'), nullable=True)
  status = Column(Boolean, index=False)
  # will be better idea to use this column for soft deletion
  end_date = Column(Date, nullable=True, index=False)
  parent = relationship("Task", remote_side=[id])
