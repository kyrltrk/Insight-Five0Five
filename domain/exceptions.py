class DomainError(Exception):
    pass


class ApiCaidaError(DomainError):
    def __init__(self, message="La API del Banco Mundial no esta disponible."):
        self.message = message
        super().__init__(self.message)


class DatosNoEncontradosError(DomainError):
    def __init__(self, message="No hay datos disponibles de ninguna fuente."):
        self.message = message
        super().__init__(self.message)


class EsquemaNoEncontradoError(DomainError):
    def __init__(self, message="El archivo de esquema SQL no fue encontrado."):
        self.message = message
        super().__init__(self.message)


class ErrorValidacion(DomainError):
    def __init__(self, message="Error en la validacion de datos."):
        self.message = message
        super().__init__(self.message)
