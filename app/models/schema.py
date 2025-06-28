from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from ..database import Base


class ProductGroup(Base):
    __tablename__ = "product_groups"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    grades = relationship("SteelGrade", back_populates="product_group")


class SteelGrade(Base):
    __tablename__ = "steel_grades"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    product_group_id = Column(Integer, ForeignKey("product_groups.id"))

    product_group = relationship("ProductGroup", back_populates="grades")
    productions = relationship("HistoricalProduction", back_populates="grade")


class HistoricalProduction(Base):
    __tablename__ = "historical_production"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    tons = Column(Integer)
    grade_id = Column(Integer, ForeignKey("steel_grades.id"))

    grade = relationship("SteelGrade", back_populates="productions")


class ForecastedProduction(Base):
    __tablename__ = "forecasted_production"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)  # Day or month for forecast
    heats = Column(Integer, nullable=False)  # Number of heats forecasted
    product_group_id = Column(Integer, ForeignKey("product_groups.id"), nullable=False)

    product_group = relationship("ProductGroup", backref="forecasted_production")


class DailyProductionSchedule(Base):
    __tablename__ = "daily_production_schedule"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    start_time = Column(String)
    mould_size = Column(String)

    grade_id = Column(Integer, ForeignKey("steel_grades.id"), nullable=False)
    grade = relationship("SteelGrade", backref="scheduled_heats")
