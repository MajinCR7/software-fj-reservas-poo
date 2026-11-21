"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - Fase 4 (Práctica Simulada)
Gestión en memoria mediante objetos y listas (sin base de datos),
con registro de eventos y errores en archivo de logs.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import os


# =====================================================================
# 1. SISTEMA DE LOGS Y EXCEPCIONES PERSONALIZADAS
# =====================================================================

ARCHIVO_LOG = "logs_software_fj.txt"


def registrar_log(nivel: str, mensaje: str) -> None:
    """Registra eventos y errores con marca de tiempo en el archivo de logs."""
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{marca_tiempo}] [{nivel}] {mensaje}\n"
    try:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as archivo:
            archivo.write(linea)
    except OSError as error_archivo:
        # Si falla la escritura del log, no detenemos el sistema principal
        print(f"[AVISO LOG] No se pudo escribir en {ARCHIVO_LOG}: {error_archivo}")


class ErrorSoftwareFJ(Exception):
    """Excepción base personalizada para el sistema de Software FJ."""


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato de entrada no cumple las reglas de validación."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta usar un servicio no disponible."""


class OperacionReservaError(ErrorSoftwareFJ):
    """Se lanza cuando ocurre un error al crear, confirmar o cancelar una reserva."""


class CalculoFinancieroError(ErrorSoftwareFJ):
    """Se lanza cuando hay inconsistencias en tarifas, descuentos, impuestos o duración."""


# =====================================================================
# 2. CLASE ABSTRACTA BASE Y CLASE CLIENTE (ENCAPSULACIÓN Y VALIDACIÓN)
# =====================================================================

class EntidadSistema(ABC):
    """Clase abstracta base para entidades generales del sistema."""

    def __init__(self, id_entidad: str) -> None:
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise DatoInvalidoError("El ID de la entidad debe ser un texto no vacío.")
        self._id_entidad = id_entidad.strip().upper()

    @property
    def id_entidad(self) -> str:
        """Retorna el identificador único de la entidad."""
        return self._id_entidad

    @abstractmethod
    def resumen(self) -> str:
        """Retorna una descripción resumida de la entidad."""


class Cliente(EntidadSistema):
    """Representa un cliente con datos personales encapsulados y validados."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(id_cliente)
        # Se asignan mediante propiedades para ejecutar validaciones estrictas
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        limpio = str(valor).strip()
        if not limpio.isdigit() or len(limpio) < 7:
            raise DatoInvalidoError(f"Teléfono inválido: '{valor}'. Debe tener al menos 7 dígitos.")
        self._telefono = limpio

    def resumen(self) -> str:
        """Implementación del método abstracto para describir al cliente."""
        return f"Cliente [{self.id_entidad}] - {self.nombre} | Correo: {self.correo} | Tel: {self.telefono}"


# =====================================================================
# 3. CLASE ABSTRACTA SERVICIO Y SUBCLASES (HERENCIA Y POLIMORFISMO)
# =====================================================================

class Servicio(EntidadSistema):
    """Clase abstracta que define el contrato de un servicio de Software FJ."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio)
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatoInvalidoError("La tarifa base del servicio debe ser mayor que cero.")
        if not isinstance(disponible, bool):
            raise DatoInvalidoError("El estado de disponibilidad debe ser booleano (True/False).")

        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        if not isinstance(estado, bool):
            raise DatoInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = estado

    @abstractmethod
    def validar_parametros(self, duracion: int) -> None:
        """Valida parámetros específicos (como duración) según el tipo de servicio."""

    @abstractmethod
    def calcular_costo_base(self, duracion: int) -> float:
        """Calcula el costo sin extras según el tipo de servicio."""

    @abstractmethod
    def describir_servicio(self) -> str:
        """Describe las características particulares del servicio."""

    def calcular_costo(
        self,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
        cargo_adicional: float = 0.0,
    ) -> float:
        """
        Simula sobrecarga de métodos mediante parámetros opcionales:
        - Solo duración: calcular_costo(duracion)
        - Con descuento: calcular_costo(duracion, descuento_pct=10)
        - Con impuesto y cargo adicional: calcular_costo(duracion, descuento_pct=5, impuesto_pct=19, cargo_adicional=20000)
        """
        try:
            self.validar_parametros(duracion)
            if not all(isinstance(x, (int, float)) for x in (descuento_pct, impuesto_pct, cargo_adicional)):
                raise CalculoFinancieroError("Los porcentajes y cargos deben ser valores numéricos.")
            if not (0.0 <= descuento_pct < 100.0):
                raise CalculoFinancieroError("El descuento debe estar entre 0% y menos del 100%.")
            if impuesto_pct < 0.0 or cargo_adicional < 0.0:
                raise CalculoFinancieroError("El impuesto y el cargo adicional no pueden ser negativos.")

            subtotal = self.calcular_costo_base(duracion) + float(cargo_adicional)
            con_descuento = subtotal * (1.0 - float(descuento_pct) / 100.0)
            total = con_descuento * (1.0 + float(impuesto_pct) / 100.0)
            return round(total, 2)
        except ErrorSoftwareFJ:
            raise
        except Exception as exc:
            raise CalculoFinancieroError("Error inesperado al calcular el costo del servicio.") from exc

    def resumen(self) -> str:
        estado_txt = "Disponible" if self.disponible else "No disponible"
        return f"{self.describir_servicio()} | Estado: {estado_txt}"


class ReservaSala(Servicio):
    """Servicio de reserva de salas para reuniones o capacitaciones."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad_personas = capacidad_personas

    def validar_parametros(self, duracion: int) -> None:
        # La duración en salas se mide en horas (mínimo 1 hora, máximo 12 horas por sesión)
        if not isinstance(duracion, int) or duracion < 1 or duracion > 12:
            raise DatoInvalidoError("La reserva de sala requiere entre 1 y 12 horas.")

    def calcular_costo_base(self, duracion: int) -> float:
        return self.tarifa_base * duracion

    def describir_servicio(self) -> str:
        return f"Sala [{self.id_servicio}] '{self.nombre}' (Capacidad: {self.capacidad_personas} personas, Tarifa/h: ${self.tarifa_base:,.2f})"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos tecnológicos."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        tipo_equipo: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise DatoInvalidoError("El tipo de equipo es obligatorio.")
        self.tipo_equipo = tipo_equipo.strip()

    def validar_parametros(self, duracion: int) -> None:
        # La duración en alquiler de equipos se mide en días (1 a 30 días)
        if not isinstance(duracion, int) or duracion < 1 or duracion > 30:
            raise DatoInvalidoError("El alquiler de equipo debe ser de 1 a 30 días.")

    def calcular_costo_base(self, duracion: int) -> float:
        # Pequeño descuento automático si el alquiler supera 5 días
        bruto = self.tarifa_base * duracion
        if duracion > 5:
            bruto *= 0.95
        return bruto

    def describir_servicio(self) -> str:
        return f"Equipo [{self.id_servicio}] '{self.nombre}' ({self.tipo_equipo}, Tarifa/día: ${self.tarifa_base:,.2f})"


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría técnica o de software especializada."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatoInvalidoError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion: int) -> None:
        # Sesiones de asesoría entre 1 y 8 horas
        if not isinstance(duracion, int) or duracion < 1 or duracion > 8:
            raise DatoInvalidoError("La asesoría especializada admite sesiones de 1 a 8 horas.")

    def calcular_costo_base(self, duracion: int) -> float:
        return self.tarifa_base * duracion

    def describir_servicio(self) -> str:
        return f"Asesoría [{self.id_servicio}] '{self.nombre}' (Área: {self.especialidad}, Tarifa/h: ${self.tarifa_base:,.2f})"


# =====================================================================
# 4. CLASE RESERVA Y GESTOR DEL SISTEMA (LISTAS INTERNAS Y EXCEPCIONES)
# =====================================================================

class Reserva:
    """Integra un cliente, un servicio, duración y estado de reserva."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> None:
        if not isinstance(id_reserva, str) or not id_reserva.strip():
            raise DatoInvalidoError("El ID de la reserva no puede estar vacío.")
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Debe asignarse un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Debe asignarse un objeto Servicio válido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible actualmente.")

        self.id_reserva = id_reserva.strip().upper()
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.descuento_pct = descuento_pct
        self.impuesto_pct = impuesto_pct
        self.estado = "PENDIENTE"
        self.total_calculado = self.servicio.calcular_costo(
            duracion=self.duracion,
            descuento_pct=self.descuento_pct,
            impuesto_pct=self.impuesto_pct,
        )

    def confirmar(self) -> None:
        """Confirma una reserva pendiente."""
        if self.estado == "CANCELADA":
            raise OperacionReservaError(f"No se puede confirmar la reserva {self.id_reserva} porque está CANCELADA.")
        if self.estado == "PROCESADA":
            raise OperacionReservaError(f"La reserva {self.id_reserva} ya fue PROCESADA.")
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio {self.servicio.nombre} dejó de estar disponible.")
        self.estado = "CONFIRMADA"

    def cancelar(self, motivo: str = "Cancelación solicitada") -> None:
        """Cancela una reserva si aún no fue procesada."""
        if self.estado == "PROCESADA":
            raise OperacionReservaError(f"No se puede cancelar la reserva {self.id_reserva}: ya fue PROCESADA.")
        self.estado = "CANCELADA"
        self.motivo_cancelacion = motivo

    def procesar(self) -> float:
        """Procesa una reserva confirmada y retorna el monto final."""
        if self.estado != "CONFIRMADA":
            raise OperacionReservaError(
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual de {self.id_reserva}: {self.estado}."
            )
        # Recalcula por seguridad encadenando excepciones si algo falla
        try:
            self.total_calculado = self.servicio.calcular_costo(
                duracion=self.duracion,
                descuento_pct=self.descuento_pct,
                impuesto_pct=self.impuesto_pct,
            )
        except Exception as exc:
            raise OperacionReservaError(f"Fallo al procesar financieramente la reserva {self.id_reserva}.") from exc

        self.estado = "PROCESADA"
        return self.total_calculado

    def __str__(self) -> str:
        return (
            f"Reserva [{self.id_reserva}] | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} | "
            f"Total: ${self.total_calculado:,.2f} | Estado: {self.estado}"
        )


class GestorSoftwareFJ:
    """Administra clientes, servicios y reservas en memoria usando listas."""

    def __init__(self) -> None:
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, cliente: Cliente) -> None:
        if any(c.id_entidad == cliente.id_entidad for c in self.clientes):
            raise DatoInvalidoError(f"Ya existe un cliente registrado con ID {cliente.id_entidad}.")
        self.clientes.append(cliente)

    def registrar_servicio(self, servicio: Servicio) -> None:
        if any(s.id_entidad == servicio.id_entidad for s in self.servicios):
            raise DatoInvalidoError(f"Ya existe un servicio registrado con ID {servicio.id_entidad}.")
        self.servicios.append(servicio)

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        for cliente in self.clientes:
            if cliente.id_entidad == id_cliente.strip().upper():
                return cliente
        raise DatoInvalidoError(f"Cliente con ID '{id_cliente}' no encontrado.")

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        for servicio in self.servicios:
            if servicio.id_entidad == id_servicio.strip().upper():
                return servicio
        raise ServicioNoDisponibleError(f"Servicio con ID '{id_servicio}' no encontrado.")

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> Reserva:
        try:
            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(id_servicio)
            reserva = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
            )
            self.reservas.append(reserva)
            return reserva
        except ErrorSoftwareFJ:
            raise
        except Exception as exc:
            # Encadenamiento explícito de excepciones
            raise OperacionReservaError(f"Error inesperado al crear la reserva '{id_reserva}'.") from exc


# =====================================================================
# 5. SIMULACIÓN DE OPERACIONES (MÍNIMO 10 OPERACIONES COMPLETAS)
# =====================================================================

def ejecutar_operacion(numero: int, descripcion: str, accion) -> None:
    """
    Ejecuta una operación de simulación usando try / except / else / finally
    para demostrar robustez y registro continuo en logs.
    """
    print(f"\n--- Operación {numero}: {descripcion} ---")
    exito = False
    try:
        resultado = accion()
    except ErrorSoftwareFJ as err_sistema:
        mensaje = f"Op {numero} ({descripcion}) -> Error controlado [{type(err_sistema).__name__}]: {err_sistema}"
        print("[ERROR CONTROLADO]", err_sistema)
        registrar_log("ERROR", mensaje)
    except Exception as err_general:
        # Encadenamos a excepción del dominio para mantener coherencia en el sistema
        envuelta = OperacionReservaError(f"Fallo no previsto en Op {numero}: {err_general}")
        mensaje = f"Op {numero} ({descripcion}) -> Excepción encadenada: {envuelta} (Causa: {err_general})"
        print("[EXCEPCIÓN ENCADENADA]", mensaje)
        registrar_log("CRITICAL", mensaje)
    else:
        exito = True
        detalle = resultado if resultado is not None else "Completada sin errores."
        print("[ÉXITO]", detalle)
        registrar_log("INFO", f"Op {numero} ({descripcion}) -> {detalle}")
    finally:
        estado_final = "OK" if exito else "CON_ERROR_MANEJADO"
        registrar_log("AUDITORIA", f"Fin de Operación {numero} | Estado: {estado_final}")


def simular_sistema_software_fj() -> None:
    """Ejecuta al menos 12 operaciones variadas para probar el sistema completo."""
    gestor = GestorSoftwareFJ()
    registrar_log("INFO", "Inicio de simulación del sistema Software FJ.")

    # Op 1: Registro válido de cliente
    def op1():
        c1 = Cliente("CLI-01", "Cristian Majin", "cristian@example.com", "3105551234")
        gestor.registrar_cliente(c1)
        return c1.resumen()

    # Op 2: Registro inválido de cliente (correo y teléfono incorrectos)
    def op2():
        c_malo = Cliente("CLI-02", "Ana", "correo_sin_arroba", "123")
        gestor.registrar_cliente(c_malo)
        return c_malo.resumen()

    # Op 3: Segundo cliente válido
    def op3():
        c2 = Cliente("CLI-03", "Dali Velasco", "dali@example.com", "3159876543")
        gestor.registrar_cliente(c2)
        return c2.resumen()

    # Op 4: Creación válida de servicio de ReservaSala
    def op4():
        s1 = ReservaSala("SRV-SALA1", "Sala de Conferencias A", 80000, capacidad_personas=20, disponible=True)
        gestor.registrar_servicio(s1)
        return s1.resumen()

    # Op 5: Creación válida de AlquilerEquipo y AsesoriaEspecializada
    def op5():
        s2 = AlquilerEquipo("SRV-EQ1", "Portátil Empresarial i7", 45000, "Laptop", disponible=True)
        s3 = AsesoriaEspecializada("SRV-ASE1", "Arquitectura Python y POO", 120000, "Backend & POO", disponible=False)
        gestor.registrar_servicio(s2)
        gestor.registrar_servicio(s3)
        return f"Registrados: {s2.id_entidad} y {s3.id_entidad} (no disponible)"

    # Op 6: Creación incorrecta de servicio (tarifa negativa / duración inválida)
    def op6():
        s_malo = ReservaSala("SRV-ERR", "Sala Inválida", -5000, capacidad_personas=10)
        gestor.registrar_servicio(s_malo)
        return s_malo.resumen()

    # Op 7: Reserva exitosa con cálculo de costo (descuento e impuesto)
    def op7():
        res1 = gestor.crear_reserva("RES-001", "CLI-01", "SRV-SALA1", duracion=3, descuento_pct=10, impuesto_pct=19)
        res1.confirmar()
        total_cobrado = res1.procesar()
        return f"{res1} | Cobrado: ${total_cobrado:,.2f}"

    # Op 8: Reserva exitosa de alquiler de equipo con método sobrecargado (solo duración)
    def op8():
        res2 = gestor.crear_reserva("RES-002", "CLI-03", "SRV-EQ1", duracion=6)
        res2.confirmar()
        return str(res2)

    # Op 9: Reserva fallida por servicio no disponible
    def op9():
        return str(gestor.crear_reserva("RES-003", "CLI-01", "SRV-ASE1", duracion=2))

    # Op 10: Reserva fallida por duración fuera de rango para sala (20 horas)
    def op10():
        return str(gestor.crear_reserva("RES-004", "CLI-01", "SRV-SALA1", duracion=20))

    # Op 11: Reserva fallida por intentar procesar una reserva cancelada
    def op11():
        res_temp = gestor.crear_reserva("RES-005", "CLI-03", "SRV-EQ1", duracion=2)
        res_temp.cancelar("Cambio de agenda")
        return str(res_temp.procesar())

    # Op 12: Reserva fallida por cliente inexistente
    def op12():
        return str(gestor.crear_reserva("RES-006", "CLI-999", "SRV-EQ1", duracion=1))

    operaciones = [
        (1, "Registro válido de cliente", op1),
        (2, "Registro inválido de cliente", op2),
        (3, "Registro válido de segundo cliente", op3),
        (4, "Creación válida de servicio de sala", op4),
        (5, "Creación de servicios de equipo y asesoría", op5),
        (6, "Creación incorrecta de servicio", op6),
        (7, "Reserva exitosa y procesada con descuento e IVA", op7),
        (8, "Reserva exitosa de alquiler con parámetros por defecto", op8),
        (9, "Reserva fallida por servicio no disponible", op9),
        (10, "Reserva fallida por duración inválida", op10),
        (11, "Reserva fallida al procesar reserva cancelada", op11),
        (12, "Reserva fallida por cliente inexistente", op12),
    ]

    for num, desc, fn in operaciones:
        ejecutar_operacion(num, desc, fn)

    print("\n=== RESUMEN FINAL EN MEMORIA ===")
    print(f"Clientes registrados: {len(gestor.clientes)}")
    print(f"Servicios registrados: {len(gestor.servicios)}")
    print(f"Reservas creadas: {len(gestor.reservas)}")
    for r in gestor.reservas:
        print("  *", r)

    if os.path.exists(ARCHIVO_LOG):
        print(f"\nArchivo de logs generado: '{ARCHIVO_LOG}'")


if __name__ == "__main__":
    simular_sistema_software_fj()
