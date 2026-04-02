from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.models.config_horario import ConfigHorario
from app.repositories.base_repositorie import BaseRepository


class ConfigHorarioRepository(BaseRepository[ConfigHorario]):
    """Repository específico para ConfigHorario"""
    
    def __init__(self, db: Session):
        super().__init__(ConfigHorario, db)
    
    def get_activos(self, skip: int = 0, limit: int = 100) -> List[ConfigHorario]:
        """Obtener configuraciones activas (estado=True)"""
        return self.db.query(self.model).filter(
            self.model.estado == True
        ).offset(skip).limit(limit).all()
    
    def get_vigente(self) -> Optional[ConfigHorario]:
        """Obtener configuración vigente (hoy está entre aplica_desde y aplica_hasta)"""
        from datetime import date as date_class
        today = date_class.today()
        return self.db.query(self.model).filter(
            (self.model.aplica_desde <= today) &
            (self.model.aplica_hasta >= today) &
            (self.model.estado == True)
        ).first()
    
    def get_en_fecha(self, fecha: date) -> Optional[ConfigHorario]:
        """Obtener configuración vigente en una fecha específica"""
        return self.db.query(self.model).filter(
            (self.model.aplica_desde <= fecha) &
            (self.model.aplica_hasta >= fecha) &
            (self.model.estado == True)
        ).first()
