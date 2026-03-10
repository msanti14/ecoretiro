from fastapi import HTTPException, status

class EcoRetiroExceptions:

    # 404 - No encontrado
    REQUEST_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Solicitud no encontrada"
    )
    USER_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )
    NOTIFICATION_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Notificación no encontrada"
    )

    # 400 - Bad request
    INVALID_STATUS_TRANSITION = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Transición de estado no permitida"
    )

    # 401 - No autenticado
    INVALID_CREDENTIALS = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"}
    )
    TOKEN_EXPIRED = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # 403 - Sin permisos
    NOT_ENOUGH_PERMISSIONS = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tenés permisos para realizar esta acción"
    )

    # 409 - Conflicto
    EMAIL_ALREADY_EXISTS = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="El email ya está registrado"
    )