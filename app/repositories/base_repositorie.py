from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.inspection import inspect

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Repository genérico para operaciones CRUD básicas"""
    
    def __init__(self, model: type[T], db: Session):
        """
        Args:
            model: Modelo SQLAlchemy
            db: Sesión de base de datos
        """
        self.model = model
        self.db = db
        self._pk_column = self._get_primary_key()
    
    def _get_primary_key(self):
        """Detectar dinámicamente la columna de clave primaria"""
        mapper = inspect(self.model)
        pk_columns = mapper.primary_key
        if pk_columns:
            return pk_columns[0]
        raise Exception(f"No se encontró clave primaria en {self.model.__name__}")
    
    def create(self, obj_in: dict) -> T:
        """Crear un nuevo registro"""
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear: {str(e)}")
    
    def get_by_id(self, obj_id: int) -> Optional[T]:
        """Obtener un registro por ID (usa la PK detectada)"""
        try:
            return self.db.query(self.model).filter(self._pk_column == obj_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener: {str(e)}")
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Obtener todos los registros con paginación"""
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener: {str(e)}")
    
    def update(self, obj_id: int, obj_in: dict) -> Optional[T]:
        """Actualizar un registro"""
        try:
            db_obj = self.get_by_id(obj_id)
            if not db_obj:
                return None
            
            for key, value in obj_in.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al actualizar: {str(e)}")
    
    def delete(self, obj_id: int) -> bool:
        """Eliminar un registro"""
        try:
            db_obj = self.get_by_id(obj_id)
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al eliminar: {str(e)}")
    
    def count(self) -> int:
        """Contar total de registros"""
        try:
            return self.db.query(self.model).count()
        except SQLAlchemyError as e:
            raise Exception(f"Error al contar: {str(e)}")
