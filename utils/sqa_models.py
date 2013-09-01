#=============================================================
# c:/1work/Python/djcode/fsis2/utils/fsis2_sqlalch.py
# Created: 29 Aug 2013 08:44:55

#
# DESCRIPTION:
#
# This files contain all of the sqlalchemy models for the fsis2
# database. The models in this files are used by the associated script
# to migrate the data from FS_master.mdb to the fsis2 database where
# it can be used by the fsis2 web app.
#
# There is some care and feeding required to ensure that the models in
# this file remain in sync with those in ~/fsis2/models.py (which
# should be considered definative).
#
# A. Cottrill
#=============================================================


import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, Date, DateTime, ForeignKey,
                        Float)
from sqlalchemy.orm import relationship, backref

import datetime

Base = declarative_base()


class BuildDate(Base):
    __tablename__ = 'fsis2_builddate'

    id = Column(Integer, primary_key=True)
    #build_date = Column(DateTime, timezone=True)
    build_date = Column(DateTime)

    def __repr__(self):
        return "<%s>" % self.build_date


class Readme(Base):
    __tablename__ = 'fsis2_readme'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    comment = Column(String)
    initials = Column(String)

    def __repr__(self):
        return "<%s>" % self.comment


class Species(Base):
    __tablename__ = 'fsis2_species'
    #__table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    species_code = Column(Integer)
    common_name = Column(String)
    scientific_name = Column(String)

    strains = relationship("Strain", order_by="Strain.id", backref="species")
    #lot = relationship("Lot", backref=backref('species', order_by=id))

    def __repr__(self):
        return "<%s (%s)>" % (self.common_name, self.scientific_name)

class Strain(Base):
    __tablename__= 'fsis2_strain'
    #__table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    species_id = Column(Integer, ForeignKey('fsis2_species.id'))
    sto_code = Column(String(5))
    strain_code = Column(String(5))
    strain_name = Column(String(20))

    #species = relationship("Species", backref=backref('strain', order_by=id))
    #lot = relationship("Lot", backref=backref('strain', order_by=id))

    def __repr__(self):
        return "<%s %s>" % (self.strain_name, self.species.common_name)



class Proponent(Base):
    __tablename__='fsis2_proponent'

    id = Column(Integer, primary_key=True)
    abbrev = Column(String(7), unique=True)
    proponent_name = Column(String(50))

    #lot = relationship("Lot", backref=backref('proponent', order_by=id))

    def __repr__(self):
        return "<%s (%s)>" % (self.proponent_name, self.abbrev)


class StockingSite(Base):
    __tablename__='fsis2_stockingsite'

    #many of these should be choice fields or foreign keys to look-up tables
    #eventually they will be replaced with spatail queries
    id = Column(Integer, primary_key=True)
    fsis_site_id =  Column(Integer, unique=True)
    site_name = Column(String(50)) #this should be unique too
    stkwby  = Column(String(30))
    stkwby_lid = Column(Integer)
    utm  = Column(String(20))
    grid = Column(String(4))
    dd_lat = Column(Float)
    dd_lon = Column(Float)
    basin = Column(String(15))
    deswby_lid  = Column(String(15))
    deswby  = Column(String(10))

    def __repr__(self):
        return "<%s (%s)>" % (self.site_name, self.site_id)


class Lot(Base):

    __tablename__='fsis2_lot'
    #__table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    #prj_cd = Column(String(13))
    fs_lot  = Column(Integer)
    spawn_year = Column(Integer)
    rearloc = Column(String(30))
    rearloc_nm = Column(String(30))
    proponent_type = Column(String())

    species_id = Column(Integer, ForeignKey('fsis2_species.id'))
    strain_id = Column(Integer, ForeignKey('fsis2_strain.id'))
    proponent_id = Column(Integer, ForeignKey('fsis2_proponent.id'))

    species = relationship("Species", order_by="Species.id", backref="species")
    strain = relationship("Strain", order_by="Strain.id", backref="strain")
    proponent = relationship("Proponent", order_by="Proponent.id",
                            backref="proponent")

    def __repr__(self):
        return "%s (%s yc %s)" % (self.fs_lot, self.spawn_year,
                                  self.species.common_name)


class Event(Base):
    __tablename__='fsis2_event'
    #__table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    prj_cd =  Column(String(13))
    fs_event = Column(Integer, unique=True)
    lotsam = Column(String(8))
    #event_date = Column(Date)
    event_date = Column(DateTime(timezone=True))
    clipa = Column(String(3))
    fish_age = Column(Integer)
    stkcnt = Column(Integer)
    fish_wt = Column(Float)
    record_biomass_calc = Column(Float)
    reartem = Column(Float)
    sitem = Column(Float)
    transit_mortality_count = Column(Integer)
    dd_lat = Column(Float)
    dd_lon = Column(Float)
    development_stage = Column(Integer)
    transit = Column(String(10))
    stocking_method = Column(String(10))
    stocking_purpose = Column(String(10))

    site_id = Column(Integer, ForeignKey('fsis2_stockingsite.id'))
    lot_id = Column(Integer, ForeignKey('fsis2_lot.id'))

    site = relationship("StockingSite", order_by="StockingSite.id",
                        backref="site")
    lot = relationship("Lot", order_by="Lot.id", backref="lot")

    def __repr__(self):
        return "%s (%s stocked on %s)" % (self.fs_event,
                                          self.lot.species.common_name,
                                          self.event_date)



class TaggingEvent(Base):

    __tablename__='fsis2_taggingevent'

    id = Column(Integer, primary_key=True)

    stocking_event_id = Column(Integer, ForeignKey('fsis2_event.id'))
    stocking_event = relationship("Event", order_by="Event.id",
                            backref="tagging_event")

    fs_tagging_event_id = Column(Integer, unique=True)
    retention_rate_pct = Column(Float)
    retention_rate_sample_size = Column(Integer)
    retention_rate_pop_size = Column(Integer)
    comments = Column(String)
    tag_type =  Column(Integer)
    tag_position =  Column(Integer)
    tag_origins =  Column(String(4))
    tag_colour =  Column(String(3))

    def __repr__(self):
        return '<fs tagging event :%s>' % self.fs_tagging_event_id

    
class CWTs_Applied(Base):

    __tablename__='fsis2_cwts_applied'

    id = Column(Integer, primary_key=True)
    tagging_event_id = Column(Integer, ForeignKey('fsis2_taggingevent.id'))
    tagging_event = relationship("TaggingEvent",
                                 backref="cwts")
    fs_tagging_event_id = Column(Integer, unique=True)
    cwt = Column(String(6))

    def __repr__(self):
        string = '-'.join((self.cwt[:2], self.cwt[2:4], self.cwt[4:]))
        return string
