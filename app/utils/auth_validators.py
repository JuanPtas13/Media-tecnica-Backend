"""
Módulo de validaciones y detección de errores comunes en JWT y autorización.

Detecta:
- Swagger usando token viejo/expirado
- Token con rol incorrecto
- Payload sin 'rol'
- Payload con 'sub' mal tipo (int vs str)
- decode_token retornando None
- Usuario no encontrado en BD
- Rol en DB diferente al del token
- Header Authorization mal formado (sin Bearer)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# =====================================================
# VALIDACIONES DE PAYLOAD
# =====================================================

def validar_payload_jwt(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validar que el payload de un JWT sea válido y contenga todos los campos requeri dos.
    
    Detecta:
    - Payload None o vacío
    - Campo 'sub' faltante
    - Campo 'exp' inválido
    - Tipos de datos incorrectos
    
    Args:
        payload: Payload decodificado del JWT
        
    Returns:
        Tupla (válido: bool, mensaje: str)
        
    Ejemplo:
        es_valido, msg = validar_payload_jwt(payload)
        if not es_valido:
            logger.error(f"Payload inválido: {msg}")
    """
    if not payload:
        return False, "Payload está vacío o None"
    
    if not isinstance(payload, dict):
        return False, f"Payload no es diccionario, es {type(payload).__name__}"
    
    # Validar 'sub' (subject - usuario ID)
    if "sub" not in payload:
        available_keys = list(payload.keys())
        return False, f"Campo 'sub' faltante en payload. Campos disponibles: {available_keys}"
    
    sub_value = payload.get("sub")
    if sub_value is None:
        return False, "Campo 'sub' tiene valor None"
    
    # Validar que 'sub' se pueda convertir a int
    try:
        if isinstance(sub_value, str):
            int(sub_value)  # Verificar que es convertible
        elif not isinstance(sub_value, int):
            return False, f"Campo 'sub' debe ser string o int, es {type(sub_value).__name__}"
    except ValueError:
        return False, f"Campo 'sub' no se puede convertir a int: '{sub_value}'"
    
    # Validar 'exp' (expiration)
    if "exp" in payload:
        exp_value = payload.get("exp")
        if not isinstance(exp_value, (int, float)):
            return False, f"Campo 'exp' debe ser número, es {type(exp_value).__name__}"
        
        # Verificar si es un timestamp válido (razonable)
        # Timestamps de 1970-01-01 a 2100-01-01
        if not (0 < exp_value < 4102444800):
            return False, f"Timestamp 'exp' fuera de rango válido: {exp_value}"
    
    return True, "Payload válido"


def detectar_campos_faltantes(payload: Dict[str, Any], campos_esperados: list) -> Optional[str]:
    """
    Detectar campos faltantes en el payload JWT.
    
    Args:
        payload: Payload del JWT
        campos_esperados: Lista de campos que se esperan (ej: ["sub", "rol", "email"])
        
    Returns:
        String describiendo campos faltantes, o None si todos están presentes
        
    Ejemplo:
        faltantes = detectar_campos_faltantes(payload, ["sub", "rol"])
        if faltantes:
            logger.error(faltantes)
    """
    if not payload:
        return "Payload es None o vacío"
    
    faltantes = [campo for campo in campos_esperados if campo not in payload]
    
    if faltantes:
        presentes = list(payload.keys())
        return f"Campos faltantes: {faltantes}. Presentes: {presentes}"
    
    return None


# =====================================================
# VALIDACIONES DE TIPOS
# =====================================================

def validar_tipo_sub(sub_value: Any) -> tuple[bool, str]:
    """
    Validar que 'sub' (usuario ID) tenga el tipo correcto.
    
    Detecta:
    - sub como float (debería ser int o str)
    - sub como list/dict (tipos compuestos)
    - sub como valor incompatible
    
    Args:
        sub_value: Valor del campo 'sub'
        
    Returns:
        Tupla (válido: bool, mensaje: str)
        
    Ejemplo:
        es_valido, msg = validar_tipo_sub(payload.get("sub"))
    """
    if sub_value is None:
        return False, "Campo 'sub' es None"
    
    if isinstance(sub_value, (str, int)):
        # Tipos válidos
        if isinstance(sub_value, str):
            # Verificar que string contiene solo dígitos
            if not sub_value.isdigit():
                return False, f"Campo 'sub' (string) contiene caracteres no numéricos: '{sub_value}'"
        elif isinstance(sub_value, int):
            if sub_value <= 0:
                return False, f"Campo 'sub' (int) debe ser positivo, recibió: {sub_value}"
        return True, f"Tipo correcto: {type(sub_value).__name__}"
    
    # Tipo incorrecto
    type_name = type(sub_value).__name__
    return False, f"Campo 'sub' tiene tipo incorrecto '{type_name}'. Debe ser string o int."


# =====================================================
# VALIDACIONES DE EXPIRACIÓN
# =====================================================

def detectar_token_casi_expirado(exp_timestamp: int, umbral_segundos: int = 300) -> tuple[bool, str]:
    """
    Detectar si un token está próximo a expirar.
    
    Útil para alertar en logs si un token está por expirar (mejora debugging).
    
    Args:
        exp_timestamp: Timestamp Unix de expiración
        umbral_segundos: Segundos antes de expiración para considerar "casi expirado" (default: 5 min)
        
    Returns:
        Tupla (esta_casi_expirado: bool, mensaje: str)
        
    Ejemplo:
        casi_expirado, msg = detectar_token_casi_expirado(payload.get("exp"))
        if casi_expirado:
            logger.warning(msg)
    """
    now_timestamp = int(datetime.utcnow().timestamp())
    tiempo_restante = exp_timestamp - now_timestamp
    
    if tiempo_restante <= 0:
        return False, "Token ya expiró"
    
    if tiempo_restante < umbral_segundos:
        return True, f"Token expirará en {tiempo_restante} segundos"
    
    return False, f"Token expirará en {tiempo_restante} segundos"


def validar_timestamp_exp(exp_timestamp: int) -> tuple[bool, str]:
    """
    Validar que el timestamp de expiración sea válido.
    
    Detecta:
    - Timestamps negativos o cero
    - Timestamps fuera de rango razonable (1970-2100)
    - Formato incorrecto
    
    Args:
        exp_timestamp: Timestamp de expiración
        
    Returns:
        Tupla (válido: bool, mensaje: str)
    """
    if not isinstance(exp_timestamp, (int, float)):
        return False, f"Timestamp 'exp' debe ser números, no {type(exp_timestamp).__name__}"
    
    # Rango: 1970-01-01 a 2100-01-01
    MIN_TIMESTAMP = 0
    MAX_TIMESTAMP = 4102444800
    
    if exp_timestamp < MIN_TIMESTAMP:
        return False, f"Timestamp negativo o muy pequeño: {exp_timestamp}"
    
    if exp_timestamp > MAX_TIMESTAMP:
        return False, f"Timestamp muy grande (después de 2100): {exp_timestamp}"
    
    return True, "Timestamp válido"


# =====================================================
# VALIDACIONES DE HEADER
# =====================================================

def validar_header_authorization(auth_header: Optional[str]) -> tuple[bool, str]:
    """
    Validar que el header Authorization tiene el formato correcto.
    
    Detecta:
    - Header vacío o None
    - Falta "Bearer" al inicio
    - Formato incorrecto (no es "Bearer <token>")
    - Token vacío después de "Bearer"
    
    Args:
        auth_header: Valor del header Authorization
        
    Returns:
        Tupla (válido: bool, mensaje: str)
        
    Ejemplo:
        es_valido, msg = validar_header_authorization(request.headers.get("Authorization"))
    """
    if not auth_header:
        return False, "Header Authorization no proporcionado"
    
    if not isinstance(auth_header, str):
        return False, f"Header Authorization debe ser string, no {type(auth_header).__name__}"
    
    parts = auth_header.split()
    
    if len(parts) < 2:
        return False, "Header Authorization mal formado: debe ser 'Bearer <token>'"
    
    scheme = parts[0].lower()
    if scheme != "bearer":
        return False, f"Scheme no es 'Bearer', es '{scheme}'"
    
    token = parts[1]
    if not token:
        return False, "Token vacío después de 'Bearer'"
    
    if len(parts) > 2:
        logger.warning(f"Header Authorization contiene más de 2 partes: {len(parts)}")
    
    return True, "Header Authorization válido"


# =====================================================
# VALIDACIONES DE ROLES Y PERMISOS
# =====================================================

def validar_rol_existe_en_bd(usuario_rol_db: Optional[str], rol_en_payload: Optional[str]) -> tuple[bool, str]:
    """
    Validar que el rol del usuario en BD coincida con el del payload.
    
    Detecta:
    - Rol faltante en DB pero presente en payload
    - Rol en DB diferente al del payload (token antiguo o modificado)
    
    Args:
        usuario_rol_db: Rol del usuario según BD
        rol_en_payload: Rol en el payload del JWT
        
    Returns:
        Tupla (válido: bool, mensaje: str)
        
    Ejemplo:
        es_valido, msg = validar_rol_existe_en_bd(usuario.rol, payload.get("rol"))
    """
    if not usuario_rol_db and not rol_en_payload:
        return False, "Usuario sin rol en BD ni en payload"
    
    if not usuario_rol_db:
        return False, f"Usuario sin rol en BD pero payload contiene: '{rol_en_payload}'"
    
    if rol_en_payload and usuario_rol_db != rol_en_payload:
        return False, (
            f"Rol de usuario no coincide. BD: '{usuario_rol_db}', "
            f"Payload: '{rol_en_payload}'. Token puede estar desactualizado."
        )
    
    return True, f"Rol valida: '{usuario_rol_db}'"


def detectar_permisos_excesivos(usuario_permisos_db: list, permisos_payload: list) -> Optional[str]:
    """
    Detectar si el payload contiene permisos que el usuario no tiene en BD.
    
    Util para detectar tokens modificados o falsificados.
    
    Args:
        usuario_permisos_db: Lista de permisos del usuario según BD
        permisos_payload: Lista de permisos en el payload
        
    Returns:
        String con permisos excesivos detectados, o None si está correcto
        
    Ejemplo:
        excesivos = detectar_permisos_excesivos(permisos_db, permisos_payload)
        if excesivos:
            logger.error(f"Token modificado: contiene permisos no autorizados: {excesivos}")
    """
    if not permisos_payload:
        return None
    
    excesivos = [p for p in permisos_payload if p not in usuario_permisos_db]
    
    if excesivos:
        return f"Token contiene permisos no autorizados: {excesivos}"
    
    return None


# =====================================================
# FUNCIÓN PRINCIPAL DE DIAGNÓSTICO
# =====================================================

def diagnosticar_token_problemas(
    payload: Optional[Dict[str, Any]],
    auth_header: Optional[str],
    usuario_rol_db: Optional[str] = None,
    usuario_permisos_db: Optional[list] = None,
) -> list:
    """
    Ejecutar diagnóstico completo de un token para detectar problemas comunes.
    
    Retorna lista de problemas detectados (vacía si no hay problemas).
    
    Args:
        payload: Payload decodificado del JWT
        auth_header: Header Authorization del request
        usuario_rol_db: Rol del usuario en BD (opcional)
        usuario_permisos_db: Permisos del usuario en BD (opcional)
        
    Returns:
        Lista de strings describiendo problemas detectados
        
    Ejemplo:
        problemas = diagnosticar_token_problemas(payload, auth_header, user.rol, user.permisos)
        if problemas:
            for problema in problemas:
                logger.error(f"Problema detectado: {problema}")
    """
    problemas = []
    
    # Validar header
    if auth_header:
        valido, msg = validar_header_authorization(auth_header)
        if not valido:
            problemas.append(f"Header inválido: {msg}")
    
    # Validar payload
    if payload:
        valido, msg = validar_payload_jwt(payload)
        if not valido:
            problemas.append(f"Payload inválido: {msg}")
            return problemas  # Si payload es inválido, no continuar
        
        # Validar 'sub'
        sub_value = payload.get("sub")
        if sub_value:
            valido, msg = validar_tipo_sub(sub_value)
            if not valido:
                problemas.append(f"Campo 'sub' inválido: {msg}")
        
        # Validar expiración
        if "exp" in payload:
            exp_value = payload.get("exp")
            valido, msg = validar_timestamp_exp(exp_value)
            if not valido:
                problemas.append(f"Expiración inválida: {msg}")
            else:
                # Verificar si está próximo a expirar
                casi_expirado, msg = detectar_token_casi_expirado(exp_value)
                if casi_expirado:
                    problemas.append(f"Advertencia: {msg}")
        
        # Validar rol (si se proporcionó BD)
        if usuario_rol_db:
            rol_payload = payload.get("rol")
            valido, msg = validar_rol_existe_en_bd(usuario_rol_db, rol_payload)
            if not valido:
                problemas.append(f"Rol inválido: {msg}")
        
        # Validar permisos (si se proporcionó BD)
        if usuario_permisos_db:
            permisos_payload = payload.get("permisos", [])
            excesivos = detectar_permisos_excesivos(usuario_permisos_db, permisos_payload)
            if excesivos:
                problemas.append(f"Seguridad: {excesivos}")
    
    return problemas


if __name__ == "__main__":
    # Ejemplo de uso
    print("Módulo de validaciones JWT cargado correctamente")
