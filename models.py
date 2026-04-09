import os  
from sqlalchemy import (
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:@localhost/postgres')
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)
Base = declarative_base()


class Identifiers(Base):
    __tablename__ = 'Identifiers'

    identifier_name = Column(String(255), primary_key=True)
    description = Column(Text)
    identifier_type = Column(String(255))

    ownership = relationship('Ownership', back_populates='identifier', cascade='all, delete-orphan')
    relationships_from = relationship(
        'Relationships',
        foreign_keys='Relationships.from_identifier_name',
        back_populates='from_identifier',
        cascade='all, delete-orphan',
    )
    relationships_to = relationship(
        'Relationships',
        foreign_keys='Relationships.to_identifier_name',
        back_populates='to_identifier',
        cascade='all, delete-orphan',
    )
    identifier_characteristics = relationship(
        'IdentifierCharacteristics',
        back_populates='identifier',
        cascade='all, delete-orphan',
    )


class Countries(Base):
    __tablename__ = 'Countries'

    name = Column(String(255), primary_key=True)
    iso_code = Column(String(255))
    short_code = Column(String(255))

    consumer_units = relationship('ConsumerUnits', back_populates='country', cascade='all, delete-orphan')


class ConsumerUnits(Base):
    __tablename__ = 'ConsumerUnits'

    number_of_consumers = Column(Integer, primary_key=True)
    country_name = Column(String(255), ForeignKey('Countries.name'), primary_key=True)

    country = relationship('Countries', back_populates='consumer_units')


class Ownership(Base):
    __tablename__ = 'Ownership'

    identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    originator_first_name = Column(String(255))
    originator_last_name = Column(String(255))
    user_id_tnumber = Column(String(255), primary_key=True)
    user_id_intranet = Column(String(255))
    email = Column(String(255))
    owner_first_name = Column(String(255))
    owner_last_name = Column(String(255))

    identifier = relationship('Identifiers', back_populates='ownership')


class Relationships(Base):
    __tablename__ = 'Relationships'

    from_identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    to_identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    relationship_name = Column(String(255))

    from_identifier = relationship(
        'Identifiers',
        foreign_keys=[from_identifier_name],
        back_populates='relationships_from',
    )
    to_identifier = relationship(
        'Identifiers',
        foreign_keys=[to_identifier_name],
        back_populates='relationships_to',
    )


class Characteristics(Base):
    __tablename__ = 'Characteristics'

    master_name = Column(String(255), primary_key=True)
    name = Column(String(255), primary_key=True)
    specifics = Column(String(255))
    action_required = Column(String(255))
    report_type = Column(String(255))
    data_type = Column(String(255))
    lower_routine_release_limit = Column(Numeric(10, 2))
    lower_limit = Column(Numeric(10, 2))
    lower_target = Column(Numeric(10, 2))
    target = Column(Numeric(10, 2))
    upper_target = Column(Numeric(10, 2))
    upper_limit = Column(Numeric(10, 2))
    upper_routine_release_limit = Column(Numeric(10, 2))
    test_frequency = Column(Integer)
    precision = Column(Integer)
    engineering_unit = Column(String(255))

    identifier_characteristics = relationship(
        'IdentifierCharacteristics',
        back_populates='characteristic',
        cascade='all, delete-orphan',
    )


class IdentifierCharacteristics(Base):
    __tablename__ = 'IdentifierCharacteristics'

    identifier_name = Column(String(255), ForeignKey('Identifiers.identifier_name'), primary_key=True)
    master_name = Column(String(255), primary_key=True)
    characteristic_name = Column(String(255), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['master_name', 'characteristic_name'],
            ['Characteristics.master_name', 'Characteristics.name'],
        ),
    )

    identifier = relationship('Identifiers', back_populates='identifier_characteristics')
    characteristic = relationship('Characteristics', back_populates='identifier_characteristics')


def create_tables() -> None:
    Base.metadata.create_all(engine)


def seed_data() -> None:
    with SessionLocal() as session:
        if session.query(Identifiers).first() is not None:
            return

        session.add_all([
            Identifiers(identifier_name='88823141', description='Shampoo Product', identifier_type='Finished Product Part'),
            Identifiers(identifier_name='88823142', description='Packaging Carton', identifier_type='Packaging Material Part'),
            Identifiers(identifier_name='88823143', description='Packaging Box', identifier_type='Packaging Material Part'),
            Identifiers(identifier_name='88823144', description='Chemical Substance', identifier_type='Assembled Product Part'),
            Identifiers(identifier_name='88823145', description='Water', identifier_type='Assembled Product Part'),
            Identifiers(identifier_name='88823146', description='Shampoo Bottle', identifier_type='Material Part'),
            Countries(name='Luxembourg', iso_code='LU', short_code='442'),
            Countries(name='France', iso_code='FR', short_code='250'),
            Countries(name='Germany', iso_code='DE', short_code='276'),
            Countries(name='Belgium', iso_code='BE', short_code='056'),
            Countries(name='Netherlands', iso_code='NL', short_code='528'),
            Countries(name='Sweden', iso_code='SE', short_code='752'),
            Countries(name='Norway', iso_code='NO', short_code='578'),
            ConsumerUnits(number_of_consumers=150, country_name='Luxembourg'),
            ConsumerUnits(number_of_consumers=200, country_name='France'),
            ConsumerUnits(number_of_consumers=100, country_name='Germany'),
            ConsumerUnits(number_of_consumers=120, country_name='Belgium'),
            ConsumerUnits(number_of_consumers=80, country_name='Netherlands'),
            ConsumerUnits(number_of_consumers=60, country_name='Sweden'),
            ConsumerUnits(number_of_consumers=90, country_name='Norway'),
            Ownership(
                identifier_name='88823141',
                originator_first_name='Andrea',
                originator_last_name='Meier',
                user_id_tnumber='AP5065',
                user_id_intranet='meier.a.1',
                email='andrea@example.com',
                owner_first_name='Andrea',
                owner_last_name='Meier',
            ),
            Ownership(
                identifier_name='88823142',
                originator_first_name='John',
                originator_last_name='Doe',
                user_id_tnumber='JD1234',
                user_id_intranet='doe.j.1',
                email='john@example.com',
                owner_first_name='John',
                owner_last_name='Doe',
            ),
            Ownership(
                identifier_name='88823143',
                originator_first_name='Jane',
                originator_last_name='Smith',
                user_id_tnumber='JS5678',
                user_id_intranet='smith.j.2',
                email='jane@example.com',
                owner_first_name='Jane',
                owner_last_name='Smith',
            ),
            Ownership(
                identifier_name='88823144',
                originator_first_name='Michael',
                originator_last_name='Brown',
                user_id_tnumber='MB9101',
                user_id_intranet='brown.m.3',
                email='michael@example.com',
                owner_first_name='Michael',
                owner_last_name='Brown',
            ),
            Ownership(
                identifier_name='88823145',
                originator_first_name='Emily',
                originator_last_name='Davis',
                user_id_tnumber='ED1123',
                user_id_intranet='davis.e.4',
                email='emily@example.com',
                owner_first_name='Emily',
                owner_last_name='Davis',
            ),
            Ownership(
                identifier_name='88823146',
                originator_first_name='David',
                originator_last_name='Wilson',
                user_id_tnumber='DW1456',
                user_id_intranet='wilson.d.5',
                email='david@example.com',
                owner_first_name='David',
                owner_last_name='Wilson',
            ),
            Relationships(from_identifier_name='88823141', to_identifier_name='88823142', relationship_name='Contains'),
            Relationships(from_identifier_name='88823141', to_identifier_name='88823143', relationship_name='Contains'),
            Relationships(from_identifier_name='88823141', to_identifier_name='88823144', relationship_name='Contains'),
            Relationships(from_identifier_name='88823141', to_identifier_name='88823145', relationship_name='Contains'),
            Relationships(from_identifier_name='88823141', to_identifier_name='88823146', relationship_name='Contains'),
            Characteristics(
                master_name='CM-10001',
                name='Volume',
                specifics='Shampoo Bottle Volume',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=490.0,
                lower_limit=490.0,
                lower_target=500.0,
                target=505.0,
                upper_target=510.0,
                upper_limit=520.0,
                upper_routine_release_limit=520.0,
                test_frequency=1,
                precision=2,
                engineering_unit='ml',
            ),
            Characteristics(
                master_name='CM-10002',
                name='pH Level',
                specifics='Shampoo pH Level',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=4.0,
                lower_limit=4.0,
                lower_target=5.0,
                target=5.5,
                upper_target=6.0,
                upper_limit=7.0,
                upper_routine_release_limit=7.0,
                test_frequency=1,
                precision=2,
                engineering_unit='pH',
            ),
            Characteristics(
                master_name='CM-10003',
                name='Viscosity',
                specifics='Shampoo Viscosity',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=10.0,
                lower_limit=10.0,
                lower_target=15.0,
                target=20.0,
                upper_target=25.0,
                upper_limit=30.0,
                upper_routine_release_limit=30.0,
                test_frequency=1,
                precision=2,
                engineering_unit='Pa.s',
            ),
            Characteristics(
                master_name='CM-10004',
                name='Color',
                specifics='Shampoo Color',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-10005',
                name='Fragrance',
                specifics='Shampoo Fragrance',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-10006',
                name='Foam Height',
                specifics='Shampoo Foam Height',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=10.0,
                lower_limit=10.0,
                lower_target=15.0,
                target=20.0,
                upper_target=25.0,
                upper_limit=30.0,
                upper_routine_release_limit=30.0,
                test_frequency=1,
                precision=2,
                engineering_unit='cm',
            ),
            Characteristics(
                master_name='CM-10007',
                name='Density',
                specifics='Shampoo Density',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=0.9,
                lower_limit=0.9,
                lower_target=1.0,
                target=1.1,
                upper_target=1.2,
                upper_limit=1.3,
                upper_routine_release_limit=1.3,
                test_frequency=1,
                precision=3,
                engineering_unit='g/cm^3',
            ),
            Characteristics(
                master_name='CM-10008',
                name='Ingredient A Concentration',
                specifics='Concentration of Ingredient A',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=0.5,
                lower_limit=0.5,
                lower_target=1.0,
                target=1.5,
                upper_target=2.0,
                upper_limit=2.5,
                upper_routine_release_limit=2.5,
                test_frequency=1,
                precision=2,
                engineering_unit='%',
            ),
            Characteristics(
                master_name='CM-10009',
                name='Ingredient B Concentration',
                specifics='Concentration of Ingredient B',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=1.0,
                lower_limit=1.0,
                lower_target=1.5,
                target=2.0,
                upper_target=2.5,
                upper_limit=3.0,
                upper_routine_release_limit=3.0,
                test_frequency=1,
                precision=2,
                engineering_unit='%',
            ),
            Characteristics(
                master_name='CM-10010',
                name='Shelf Life',
                specifics='Shelf Life of Shampoo',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=12.0,
                lower_limit=12.0,
                lower_target=18.0,
                target=24.0,
                upper_target=30.0,
                upper_limit=36.0,
                upper_routine_release_limit=36.0,
                test_frequency=1,
                precision=1,
                engineering_unit='months',
            ),
            Characteristics(
                master_name='CM-20001',
                name='Carton Thickness',
                specifics='Thickness of Carton',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=1.0,
                lower_limit=1.0,
                lower_target=1.5,
                target=2.0,
                upper_target=2.5,
                upper_limit=3.0,
                upper_routine_release_limit=3.0,
                test_frequency=1,
                precision=2,
                engineering_unit='mm',
            ),
            Characteristics(
                master_name='CM-20002',
                name='Carton Weight',
                specifics='Weight of Carton',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=50.0,
                lower_limit=50.0,
                lower_target=55.0,
                target=60.0,
                upper_target=65.0,
                upper_limit=70.0,
                upper_routine_release_limit=70.0,
                test_frequency=1,
                precision=1,
                engineering_unit='g',
            ),
            Characteristics(
                master_name='CM-20003',
                name='Carton Dimensions',
                specifics='Dimensions of Carton',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-20004',
                name='Carton Material',
                specifics='Material of Carton',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-20005',
                name='Carton Color',
                specifics='Color of Carton',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-30001',
                name='Box Thickness',
                specifics='Thickness of Box',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=2.0,
                lower_limit=2.0,
                lower_target=2.5,
                target=3.0,
                upper_target=3.5,
                upper_limit=4.0,
                upper_routine_release_limit=4.0,
                test_frequency=1,
                precision=2,
                engineering_unit='mm',
            ),
            Characteristics(
                master_name='CM-30002',
                name='Box Weight',
                specifics='Weight of Box',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=100.0,
                lower_limit=100.0,
                lower_target=110.0,
                target=120.0,
                upper_target=130.0,
                upper_limit=140.0,
                upper_routine_release_limit=140.0,
                test_frequency=1,
                precision=1,
                engineering_unit='g',
            ),
            Characteristics(
                master_name='CM-30003',
                name='Box Dimensions',
                specifics='Dimensions of Box',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-30004',
                name='Box Material',
                specifics='Material of Box',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-30005',
                name='Box Color',
                specifics='Color of Box',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-40001',
                name='Chemical Purity',
                specifics='Purity of Chemical Substance',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=95.0,
                lower_limit=95.0,
                lower_target=97.0,
                target=98.0,
                upper_target=99.0,
                upper_limit=100.0,
                upper_routine_release_limit=100.0,
                test_frequency=1,
                precision=1,
                engineering_unit='%',
            ),
            Characteristics(
                master_name='CM-40002',
                name='Chemical Concentration',
                specifics='Concentration of Chemical Substance',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=10.0,
                lower_limit=10.0,
                lower_target=15.0,
                target=20.0,
                upper_target=25.0,
                upper_limit=30.0,
                upper_routine_release_limit=30.0,
                test_frequency=1,
                precision=1,
                engineering_unit='%',
            ),
            Characteristics(
                master_name='CM-40003',
                name='Chemical pH',
                specifics='pH of Chemical Substance',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=2.0,
                lower_limit=2.0,
                lower_target=3.0,
                target=4.0,
                upper_target=5.0,
                upper_limit=6.0,
                upper_routine_release_limit=6.0,
                test_frequency=1,
                precision=2,
                engineering_unit='pH',
            ),
            Characteristics(
                master_name='CM-40004',
                name='Chemical Viscosity',
                specifics='Viscosity of Chemical Substance',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=5.0,
                lower_limit=5.0,
                lower_target=10.0,
                target=15.0,
                upper_target=20.0,
                upper_limit=25.0,
                upper_routine_release_limit=25.0,
                test_frequency=1,
                precision=2,
                engineering_unit='Pa.s',
            ),
            Characteristics(
                master_name='CM-40005',
                name='Chemical Color',
                specifics='Color of Chemical Substance',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-50002',
                name='Water pH',
                specifics='pH of Water',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=6.5,
                lower_limit=6.5,
                lower_target=7.0,
                target=7.5,
                upper_target=8.0,
                upper_limit=8.5,
                upper_routine_release_limit=8.5,
                test_frequency=1,
                precision=2,
                engineering_unit='pH',
            ),
            Characteristics(
                master_name='CM-50003',
                name='Water Conductivity',
                specifics='Conductivity of Water',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=0.0,
                lower_limit=0.0,
                lower_target=0.1,
                target=0.2,
                upper_target=0.3,
                upper_limit=0.5,
                upper_routine_release_limit=0.5,
                test_frequency=1,
                precision=3,
                engineering_unit='µS/cm',
            ),
            Characteristics(
                master_name='CM-50004',
                name='Water Hardness',
                specifics='Hardness of Water',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=0.0,
                lower_limit=0.0,
                lower_target=1.0,
                target=2.0,
                upper_target=3.0,
                upper_limit=4.0,
                upper_routine_release_limit=4.0,
                test_frequency=1,
                precision=1,
                engineering_unit='dH',
            ),
            Characteristics(
                master_name='CM-50005',
                name='Water Color',
                specifics='Color of Water',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
            Characteristics(
                master_name='CM-60001',
                name='Bottle Volume',
                specifics='Capacity of Shampoo Bottle',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=490.0,
                lower_limit=490.0,
                lower_target=500.0,
                target=505.0,
                upper_target=510.0,
                upper_limit=520.0,
                upper_routine_release_limit=520.0,
                test_frequency=1,
                precision=2,
                engineering_unit='ml',
            ),
            Characteristics(
                master_name='CM-60002',
                name='Bottle Weight',
                specifics='Weight of Shampoo Bottle',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=30.0,
                lower_limit=30.0,
                lower_target=35.0,
                target=40.0,
                upper_target=45.0,
                upper_limit=50.0,
                upper_routine_release_limit=50.0,
                test_frequency=1,
                precision=1,
                engineering_unit='g',
            ),
            Characteristics(
                master_name='CM-60003',
                name='Bottle Height',
                specifics='Height of Shampoo Bottle',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=180.0,
                lower_limit=180.0,
                lower_target=185.0,
                target=190.0,
                upper_target=195.0,
                upper_limit=200.0,
                upper_routine_release_limit=200.0,
                test_frequency=1,
                precision=1,
                engineering_unit='mm',
            ),
            Characteristics(
                master_name='CM-60004',
                name='Bottle Diameter',
                specifics='Diameter of Shampoo Bottle',
                action_required='CONTROL',
                report_type='VARIABLE',
                data_type='Decimal',
                lower_routine_release_limit=50.0,
                lower_limit=50.0,
                lower_target=55.0,
                target=60.0,
                upper_target=65.0,
                upper_limit=70.0,
                upper_routine_release_limit=70.0,
                test_frequency=1,
                precision=1,
                engineering_unit='mm',
            ),
            Characteristics(
                master_name='CM-60005',
                name='Bottle Material',
                specifics='Material of Shampoo Bottle',
                action_required='INSPECT',
                report_type='ATTRIBUTE',
                data_type='String',
                test_frequency=1,
                precision=0,
                engineering_unit='',
            ),
        ])

        session.add_all([
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10001', characteristic_name='Volume'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10002', characteristic_name='pH Level'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10003', characteristic_name='Viscosity'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10004', characteristic_name='Color'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10005', characteristic_name='Fragrance'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10006', characteristic_name='Foam Height'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10007', characteristic_name='Density'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10008', characteristic_name='Ingredient A Concentration'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10009', characteristic_name='Ingredient B Concentration'),
            IdentifierCharacteristics(identifier_name='88823141', master_name='CM-10010', characteristic_name='Shelf Life'),
            IdentifierCharacteristics(identifier_name='88823142', master_name='CM-20001', characteristic_name='Carton Thickness'),
            IdentifierCharacteristics(identifier_name='88823142', master_name='CM-20002', characteristic_name='Carton Weight'),
            IdentifierCharacteristics(identifier_name='88823142', master_name='CM-20003', characteristic_name='Carton Dimensions'),
            IdentifierCharacteristics(identifier_name='88823142', master_name='CM-20004', characteristic_name='Carton Material'),
            IdentifierCharacteristics(identifier_name='88823142', master_name='CM-20005', characteristic_name='Carton Color'),
            IdentifierCharacteristics(identifier_name='88823143', master_name='CM-30001', characteristic_name='Box Thickness'),
            IdentifierCharacteristics(identifier_name='88823143', master_name='CM-30002', characteristic_name='Box Weight'),
            IdentifierCharacteristics(identifier_name='88823143', master_name='CM-30003', characteristic_name='Box Dimensions'),
            IdentifierCharacteristics(identifier_name='88823143', master_name='CM-30004', characteristic_name='Box Material'),
            IdentifierCharacteristics(identifier_name='88823143', master_name='CM-30005', characteristic_name='Box Color'),
            IdentifierCharacteristics(identifier_name='88823144', master_name='CM-40001', characteristic_name='Chemical Purity'),
            IdentifierCharacteristics(identifier_name='88823144', master_name='CM-40002', characteristic_name='Chemical Concentration'),
            IdentifierCharacteristics(identifier_name='88823144', master_name='CM-40003', characteristic_name='Chemical pH'),
            IdentifierCharacteristics(identifier_name='88823144', master_name='CM-40004', characteristic_name='Chemical Viscosity'),
            IdentifierCharacteristics(identifier_name='88823144', master_name='CM-40005', characteristic_name='Chemical Color'),
            IdentifierCharacteristics(identifier_name='88823145', master_name='CM-50002', characteristic_name='Water pH'),
            IdentifierCharacteristics(identifier_name='88823145', master_name='CM-50003', characteristic_name='Water Conductivity'),
            IdentifierCharacteristics(identifier_name='88823145', master_name='CM-50004', characteristic_name='Water Hardness'),
            IdentifierCharacteristics(identifier_name='88823145', master_name='CM-50005', characteristic_name='Water Color'),
            IdentifierCharacteristics(identifier_name='88823146', master_name='CM-60001', characteristic_name='Bottle Volume'),
            IdentifierCharacteristics(identifier_name='88823146', master_name='CM-60002', characteristic_name='Bottle Weight'),
            IdentifierCharacteristics(identifier_name='88823146', master_name='CM-60003', characteristic_name='Bottle Height'),
            IdentifierCharacteristics(identifier_name='88823146', master_name='CM-60004', characteristic_name='Bottle Diameter'),
            IdentifierCharacteristics(identifier_name='88823146', master_name='CM-60005', characteristic_name='Bottle Material'),
        ])
        session.commit()


def main() -> None:
    create_tables()
    seed_data()
    print(f'Tables created and seeded using {DATABASE_URL}')


if __name__ == '__main__':
    main()
