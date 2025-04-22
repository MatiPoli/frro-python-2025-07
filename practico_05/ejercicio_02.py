"""Base de Datos - ORM"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ejercicio_01 import Base, Socio

from typing import List, Optional

class DatosSocio():

    def __init__(self):
        # Crear el motor de base de datos en memoria
        self.engine = create_engine('sqlite:///:memory:')
        # Crear las tablas en la base de datos
        Base.metadata.create_all(self.engine)
        # Crear una sesión para interactuar con la base de datos
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def buscar(self, id_socio: int) -> Optional[Socio]:
        """Devuelve la instancia del socio, dado su id. Devuelve None si no 
        encuentra nada.
        """
        return self.session.query(Socio).filter(Socio.id_socio == id_socio).first()

    def buscar_dni(self, dni_socio: int) -> Optional[Socio]:
        """Devuelve la instancia del socio, dado su dni. Devuelve None si no 
        encuentra nada.
        """
        return self.session.query(Socio).filter(Socio.dni == dni_socio).first()
        
    def todos(self) -> List[Socio]:
        """Devuelve listado de todos los socios en la base de datos."""
        return self.session.query(Socio).all()

    def borrar_todos(self) -> bool:
        """Borra todos los socios de la base de datos. Devuelve True si el 
        borrado fue exitoso.
        """
        return self.session.query(Socio).delete()

    def alta(self, socio: Socio) -> Socio:
        """Agrega un nuevo socio a la tabla y lo devuelve"""
        self.session.add(socio)
        self.session.commit()
        return socio

    def baja(self, id_socio: int) -> bool:
        """Borra el socio especificado por el id. Devuelve True si el borrado 
        fue exitoso.
        """
        socio = self.session.query(Socio).filter(Socio.id_socio == id_socio).first()
        if socio:
            self.session.delete(socio)
            self.session.commit()
            return True
        return False

    def modificacion(self, socio: Socio) -> Socio:
        """Guarda un socio con sus datos modificados. Devuelve el Socio 
        modificado.
        """
        socio_modificado = self.session.query(Socio).filter(Socio.id_socio == socio.id_socio).first()
        if socio_modificado:
            socio_modificado.dni = socio.dni
            socio_modificado.nombre = socio.nombre
            socio_modificado.apellido = socio.apellido
            self.session.commit()
        return socio_modificado

    def contarSocios(self) -> int:
        """Devuelve el total de socios que existen en la tabla"""
        return self.session.query(Socio).count()


# Aclaración: tuve que cambiar el id por id_socio como estaba definido en ejercicio_01.py
# NO MODIFICAR - INICIO

# Test Creación
datos = DatosSocio()

# Test Alta
socio = datos.alta(Socio(dni=12345678, nombre='Juan', apellido='Perez'))
assert socio.id_socio > 0

# Test Baja
assert datos.baja(socio.id_socio) == True

# Test Consulta
socio_2 = datos.alta(Socio(dni=12345679, nombre='Carlos', apellido='Perez'))
assert datos.buscar(socio_2.id_socio) == socio_2

# Test Buscar DNI
socio_2 = datos.alta(Socio(dni=12345670, nombre='Carlos', apellido='Perez'))
assert datos.buscar_dni(socio_2.dni) == socio_2

# Test Modificación
socio_3 = datos.alta(Socio(dni=12345680, nombre='Susana', apellido='Gimenez'))
socio_3.nombre = 'Moria'
socio_3.apellido = 'Casan'
socio_3.dni = 13264587
datos.modificacion(socio_3)
socio_3_modificado = datos.buscar(socio_3.id_socio)
assert socio_3_modificado.id_socio == socio_3.id_socio
assert socio_3_modificado.nombre == 'Moria'
assert socio_3_modificado.apellido == 'Casan'
assert socio_3_modificado.dni == 13264587

# Test Conteo
assert len(datos.todos()) == 3

# Test Delete
datos.borrar_todos()
assert len(datos.todos()) == 0

# NO MODIFICAR - FIN