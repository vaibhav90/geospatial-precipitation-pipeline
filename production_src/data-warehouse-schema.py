from sqlalchemy import create_engine, Column, Integer, Float, String, Date, DateTime, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Replace with your PostgreSQL connection string
engine = create_engine('postgresql://username:password@localhost:5432/era5_database')

Base = declarative_base()

class DimTime(Base):
    __tablename__ = 'dim_time'

    time_id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)

class DimLocation(Base):
    __tablename__ = 'dim_location'

    location_id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float)

class FactAtmospheric(Base):
    __tablename__ = 'fact_atmospheric'

    atmospheric_id = Column(Integer, primary_key=True)
    time_id = Column(Integer, ForeignKey('dim_time.time_id'), nullable=False)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False)
    temperature = Column(Float)
    pressure = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    cloud_cover = Column(Float)
    precipitation = Column(Float)

    time = relationship("DimTime")
    location = relationship("DimLocation")

class FactLandSurface(Base):
    __tablename__ = 'fact_land_surface'

    land_surface_id = Column(Integer, primary_key=True)
    time_id = Column(Integer, ForeignKey('dim_time.time_id'), nullable=False)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False)
    soil_temperature = Column(Float)
    soil_moisture = Column(Float)
    snow_depth = Column(Float)
    snow_cover = Column(Float)
    surface_pressure = Column(Float)
    evaporation = Column(Float)

    time = relationship("DimTime")
    location = relationship("DimLocation")

class FactRadiation(Base):
    __tablename__ = 'fact_radiation'

    radiation_id = Column(Integer, primary_key=True)
    time_id = Column(Integer, ForeignKey('dim_time.time_id'), nullable=False)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False)
    solar_radiation_down = Column(Float)
    thermal_radiation_down = Column(Float)
    net_solar_radiation = Column(Float)
    net_thermal_radiation = Column(Float)
    sensible_heat_flux = Column(Float)
    latent_heat_flux = Column(Float)

    time = relationship("DimTime")
    location = relationship("DimLocation")

class FactOcean(Base):
    __tablename__ = 'fact_ocean'

    ocean_id = Column(Integer, primary_key=True)
    time_id = Column(Integer, ForeignKey('dim_time.time_id'), nullable=False)
    location_id = Column(Integer, ForeignKey('dim_location.location_id'), nullable=False)
    sea_surface_temperature = Column(Float)
    wave_height = Column(Float)
    wave_direction = Column(Float)
    mixed_layer_depth = Column(Float)

    time = relationship("DimTime")
    location = relationship("DimLocation")

class MetaData(Base):
    __tablename__ = 'meta_data'

    id = Column(Integer, primary_key=True)
    table_name = Column(String, nullable=False)
    last_updated = Column(DateTime, server_default=func.now())
    row_count = Column(Integer)
    data_source = Column(String)

# Create all tables in the engine
Base.metadata.create_all(engine)

print("Schema created successfully!")