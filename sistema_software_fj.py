"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación (213023) - Fase 4 (Práctica Simulada)
Gestión en memoria mediante objetos y listas (sin base de datos),
con registro de eventos y errores en archivo de logs.
"""

from abc import ABC, abstractmethod  # ABC y abstractmethod permiten crear clases abstractas
from datetime import datetime  # datetime se usa para la marca de tiempo de los logs
import os  # os se usa para verificar que el archivo de logs exista
import re  # re permite validar el correo con una expresión regular


# =====================================================================
# 1. SISTEMA DE LOGS, VALIDADORES Y EXCEPCIONES PERSONALIZADAS
# =====================================================================

ARCHIVO_LOG = "logs_software_fj.txt"  # Nombre del archivo donde se guardan eventos y errores

# Patrón de correo: texto, una arroba, dominio y al menos un punto con extensión
PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def registrar_log(nivel: str, mensaje: str) -> None:
    """Registra eventos y errores con marca de tiempo en el archivo de logs."""
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Fecha y hora actual
    linea = f"[{marca_tiempo}] [{nivel}] {mensaje}\n"  # Línea completa que se escribirá
    try:  # Se protege la escritura: un fallo del log no debe detener el sistema
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as archivo:  # Modo "a": agrega al final
            archivo.write(linea)  # Escribe la línea en el archivo
    except OSError as error_archivo:  # Si el disco o los permisos fallan
        print(f"[AVISO LOG] No se pudo escribir en {ARCHIVO_LOG}: {error_archivo}")  # Solo avisa


def es_entero(valor) -> bool:
    """Retorna True si el valor es un entero real (excluye True/False, que en Python son int)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def es_numero(valor) -> bool:
    """Retorna True si el valor es int o float real (excluye booleanos)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


class ErrorSoftwareFJ(Exception):
    """Excepción base personalizada para el sistema de Software FJ."""


class DatoInvalidoError(ErrorSoftwareFJ):
    """Se lanza cuando un dato de entrada no cumple las reglas de validación."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Se lanza cuando se intenta usar un servicio no disponible o inexistente."""


class OperacionReservaError(ErrorSoftwareFJ):
    """Se lanza cuando ocurre un error al crear, confirmar, cancelar o procesar una reserva."""


class CalculoFinancieroError(ErrorSoftwareFJ):
    """Se lanza cuando hay inconsistencias en tarifas, descuentos, impuestos o duración."""


# =====================================================================
# 2. CLASE ABSTRACTA BASE Y CLASE CLIENTE (ENCAPSULACIÓN Y VALIDACIÓN)
# =====================================================================

class EntidadSistema(ABC):
    """Clase abstracta base para entidades generales del sistema."""

    def __init__(self, id_entidad: str) -> None:
        # El ID debe ser un texto con contenido; si no, se rechaza la entidad
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise DatoInvalidoError("El ID de la entidad debe ser un texto no vacío.")
        self._id_entidad = id_entidad.strip().upper()  # Atributo privado, siempre en mayúsculas

    @property
    def id_entidad(self) -> str:
        """Retorna el identificador único de la entidad (solo lectura)."""
        return self._id_entidad

    @abstractmethod
    def resumen(self) -> str:
        """Retorna una descripción resumida de la entidad (cada hija la implementa)."""


class Cliente(EntidadSistema):
    """Representa un cliente con datos personales encapsulados y validados."""

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(id_cliente)  # Valida y guarda el ID en la clase base
        self.nombre = nombre  # Pasa por el setter de nombre (validación)
        self.correo = correo  # Pasa por el setter de correo (validación)
        self.telefono = telefono  # Pasa por el setter de teléfono (validación)

    @property
    def nombre(self) -> str:
        """Retorna el nombre del cliente."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        # El nombre debe ser texto con al menos 3 caracteres útiles
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self._nombre = valor.strip()  # Se guarda sin espacios sobrantes

    @property
    def correo(self) -> str:
        """Retorna el correo del cliente."""
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        # El correo debe ser texto y cumplir el patrón usuario@dominio.extension
        if not isinstance(valor, str) or not PATRON_CORREO.match(valor.strip()):
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()  # Se normaliza a minúsculas

    @property
    def telefono(self) -> str:
        """Retorna el teléfono del cliente."""
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        limpio = str(valor).strip()  # Se convierte a texto y se quitan espacios
        # Solo dígitos, entre 7 y 15 caracteres
        if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
            raise DatoInvalidoError(f"Teléfono inválido: '{valor}'. Debe tener entre 7 y 15 dígitos.")
        self._telefono = limpio  # Se guarda el teléfono validado

    def resumen(self) -> str:
        """Implementación del método abstracto para describir al cliente."""
        return (
            f"Cliente [{self.id_entidad}] - {self.nombre} | "
            f"Correo: {self.correo} | Tel: {self.telefono}"
        )


# =====================================================================
# 3. CLASE ABSTRACTA SERVICIO Y SUBCLASES (HERENCIA Y POLIMORFISMO)
# =====================================================================

class Servicio(EntidadSistema):
    """Clase abstracta que define el contrato de un servicio de Software FJ."""

    unidad_tiempo = "unidades"  # Unidad de duración; cada servicio hijo la sobrescribe

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio)  # Valida y guarda el ID en la clase base
        # El nombre del servicio es obligatorio
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")
        # La tarifa debe ser numérica y mayor que cero
        if not es_numero(tarifa_base) or tarifa_base <= 0:
            raise DatoInvalidoError("La tarifa base del servicio debe ser mayor que cero.")
        # La disponibilidad solo admite True o False
        if not isinstance(disponible, bool):
            raise DatoInvalidoError("El estado de disponibilidad debe ser booleano (True/False).")

        self._nombre = nombre.strip()  # Atributo privado: nombre
        self._tarifa_base = float(tarifa_base)  # Atributo privado: tarifa por unidad de tiempo
        self._disponible = disponible  # Atributo privado: disponibilidad

    @property
    def nombre(self) -> str:
        """Retorna el nombre del servicio."""
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        """Retorna la tarifa base del servicio."""
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        """Retorna si el servicio está disponible."""
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        # Solo se acepta un booleano real
        if not isinstance(estado, bool):
            raise DatoInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = estado  # Actualiza la disponibilidad

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
        Sobrecarga mediante parámetros opcionales (forma habitual en Python):
        - Solo duración: calcular_costo(duracion)
        - Con descuento: calcular_costo(duracion, descuento_pct=10)
        - Con impuesto y cargo: calcular_costo(duracion, descuento_pct=5, impuesto_pct=19, cargo_adicional=20000)
        """
        try:
            self.validar_parametros(duracion)  # Cada servicio valida su propia duración (polimorfismo)
            # Descuento, impuesto y cargo deben ser numéricos
            if not all(es_numero(x) for x in (descuento_pct, impuesto_pct, cargo_adicional)):
                raise CalculoFinancieroError("Los porcentajes y cargos deben ser valores numéricos.")
            # El descuento debe estar en el rango [0, 100)
            if not (0.0 <= descuento_pct < 100.0):
                raise CalculoFinancieroError("El descuento debe estar entre 0% y menos del 100%.")
            # Impuesto y cargo no pueden ser negativos
            if impuesto_pct < 0.0 or cargo_adicional < 0.0:
                raise CalculoFinancieroError("El impuesto y el cargo adicional no pueden ser negativos.")

            subtotal = self.calcular_costo_base(duracion) + float(cargo_adicional)  # Costo base + cargo
            con_descuento = subtotal * (1.0 - float(descuento_pct) / 100.0)  # Se aplica el descuento
            total = con_descuento * (1.0 + float(impuesto_pct) / 100.0)  # Se aplica el impuesto
            return round(total, 2)  # Total redondeado a 2 decimales
        except ErrorSoftwareFJ:
            raise  # Los errores propios del sistema se propagan sin cambios
        except Exception as exc:  # Cualquier error inesperado se encadena a una excepción propia
            raise CalculoFinancieroError("Error inesperado al calcular el costo del servicio.") from exc

    def calcular_costo_con_impuesto(self, duracion: int, impuesto_pct: float) -> float:
        """Variante 'sobrecargada': costo con impuesto, sin descuento."""
        return self.calcular_costo(duracion, impuesto_pct=impuesto_pct)

    def calcular_costo_con_descuento(self, duracion: int, descuento_pct: float) -> float:
        """Variante 'sobrecargada': costo con descuento, sin impuesto."""
        return self.calcular_costo(duracion, descuento_pct=descuento_pct)

    def resumen(self) -> str:
        """Implementación del método abstracto de la clase base."""
        estado_txt = "Disponible" if self.disponible else "No disponible"  # Texto legible del estado
        return f"{self.describir_servicio()} | Estado: {estado_txt}"


class ReservaSala(Servicio):
    """Servicio de reserva de salas para reuniones o capacitaciones."""

    unidad_tiempo = "horas"  # Las salas se reservan por horas

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)  # Datos comunes
        # La capacidad debe ser un entero positivo
        if not es_entero(capacidad_personas) or capacidad_personas <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        self._capacidad_personas = capacidad_personas  # Atributo privado propio de la sala

    @property
    def capacidad_personas(self) -> int:
        """Retorna la capacidad de la sala."""
        return self._capacidad_personas

    def validar_parametros(self, duracion: int) -> None:
        # Una sala se reserva entre 1 y 12 horas
        if not es_entero(duracion) or duracion < 1 or duracion > 12:
            raise DatoInvalidoError("La reserva de sala requiere entre 1 y 12 horas.")

    def calcular_costo_base(self, duracion: int) -> float:
        return self.tarifa_base * duracion  # Tarifa por hora x horas

    def describir_servicio(self) -> str:
        return (
            f"Sala [{self.id_entidad}] '{self.nombre}' "
            f"(Capacidad: {self.capacidad_personas} personas, Tarifa/h: ${self.tarifa_base:,.2f})"
        )


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos tecnológicos."""

    unidad_tiempo = "días"  # Los equipos se alquilan por días

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        tipo_equipo: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)  # Datos comunes
        # El tipo de equipo es obligatorio
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise DatoInvalidoError("El tipo de equipo es obligatorio.")
        self._tipo_equipo = tipo_equipo.strip()  # Atributo privado propio del equipo

    @property
    def tipo_equipo(self) -> str:
        """Retorna el tipo de equipo."""
        return self._tipo_equipo

    def validar_parametros(self, duracion: int) -> None:
        # Un equipo se alquila entre 1 y 30 días
        if not es_entero(duracion) or duracion < 1 or duracion > 30:
            raise DatoInvalidoError("El alquiler de equipo debe ser de 1 a 30 días.")

    def calcular_costo_base(self, duracion: int) -> float:
        bruto = self.tarifa_base * duracion  # Tarifa por día x días
        if duracion > 5:  # Regla propia: más de 5 días tiene 5% de descuento
            bruto *= 0.95
        return bruto

    def describir_servicio(self) -> str:
        return (
            f"Equipo [{self.id_entidad}] '{self.nombre}' "
            f"({self.tipo_equipo}, Tarifa/día: ${self.tarifa_base:,.2f})"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría técnica o de software especializada."""

    unidad_tiempo = "horas"  # Las asesorías se miden en horas

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        especialidad: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)  # Datos comunes
        # La especialidad es obligatoria
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatoInvalidoError("La especialidad de la asesoría es obligatoria.")
        self._especialidad = especialidad.strip()  # Atributo privado propio de la asesoría

    @property
    def especialidad(self) -> str:
        """Retorna la especialidad de la asesoría."""
        return self._especialidad

    def validar_parametros(self, duracion: int) -> None:
        # Una asesoría admite sesiones de 1 a 8 horas
        if not es_entero(duracion) or duracion < 1 or duracion > 8:
            raise DatoInvalidoError("La asesoría especializada admite sesiones de 1 a 8 horas.")

    def calcular_costo_base(self, duracion: int) -> float:
        return self.tarifa_base * duracion  # Tarifa por hora x horas

    def describir_servicio(self) -> str:
        return (
            f"Asesoría [{self.id_entidad}] '{self.nombre}' "
            f"(Área: {self.especialidad}, Tarifa/h: ${self.tarifa_base:,.2f})"
        )


# =====================================================================
# 4. CLASE RESERVA Y GESTOR DEL SISTEMA (LISTAS INTERNAS Y EXCEPCIONES)
# =====================================================================

class Reserva(EntidadSistema):
    """Integra un cliente, un servicio, duración y estado de reserva."""

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.0,
    ) -> None:
        super().__init__(id_reserva)  # Valida y guarda el ID de la reserva
        # La reserva exige un Cliente real
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Debe asignarse un objeto Cliente válido.")
        # La reserva exige un Servicio real
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Debe asignarse un objeto Servicio válido.")
        # No se puede reservar un servicio no disponible
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible actualmente.")

        self._cliente = cliente  # Atributo privado: cliente
        self._servicio = servicio  # Atributo privado: servicio
        self._duracion = duracion  # Atributo privado: duración
        self._descuento_pct = descuento_pct  # Atributo privado: descuento
        self._impuesto_pct = impuesto_pct  # Atributo privado: impuesto
        self._estado = "PENDIENTE"  # Estado inicial de toda reserva
        self._motivo_cancelacion = None  # Se llena solo si la reserva se cancela
        # Se calcula el total al crear; si los datos son inválidos, lanza excepción y no se crea la reserva
        self._total_calculado = self._servicio.calcular_costo(
            duracion=self._duracion,
            descuento_pct=self._descuento_pct,
            impuesto_pct=self._impuesto_pct,
        )

    @property
    def cliente(self) -> Cliente:
        """Retorna el cliente de la reserva."""
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        """Retorna el servicio reservado."""
        return self._servicio

    @property
    def duracion(self) -> int:
        """Retorna la duración reservada."""
        return self._duracion

    @property
    def estado(self) -> str:
        """Retorna el estado actual (solo lectura: solo cambia mediante confirmar/cancelar/procesar)."""
        return self._estado

    @property
    def total_calculado(self) -> float:
        """Retorna el total calculado de la reserva."""
        return self._total_calculado

    @property
    def motivo_cancelacion(self):
        """Retorna el motivo de cancelación (None si no fue cancelada)."""
        return self._motivo_cancelacion

    def ajustar_condiciones(self, descuento_pct: float = None, impuesto_pct: float = None) -> None:
        """
        Cambia descuento/impuesto de una reserva aún no procesada.
        La validación financiera se hace al procesar, no aquí.
        """
        # Solo se puede ajustar mientras la reserva esté pendiente o confirmada
        if self._estado not in ("PENDIENTE", "CONFIRMADA"):
            raise OperacionReservaError(f"No se pueden ajustar condiciones de una reserva {self._estado}.")
        if descuento_pct is not None:  # Solo se cambia lo que se indicó
            self._descuento_pct = descuento_pct
        if impuesto_pct is not None:
            self._impuesto_pct = impuesto_pct
        registrar_log("INFO", f"Condiciones ajustadas en {self.id_entidad}.")  # Evento relevante

    def confirmar(self) -> None:
        """Confirma una reserva pendiente."""
        if self._estado == "CANCELADA":  # Una reserva cancelada no se puede confirmar
            raise OperacionReservaError(f"No se puede confirmar la reserva {self.id_entidad} porque está CANCELADA.")
        if self._estado == "PROCESADA":  # Una reserva procesada ya terminó su ciclo
            raise OperacionReservaError(f"La reserva {self.id_entidad} ya fue PROCESADA.")
        if not self._servicio.disponible:  # El servicio pudo dejar de estar disponible
            raise ServicioNoDisponibleError(f"El servicio {self._servicio.nombre} dejó de estar disponible.")
        self._estado = "CONFIRMADA"  # Cambio de estado permitido
        registrar_log("INFO", f"Reserva {self.id_entidad} confirmada.")  # Evento relevante

    def cancelar(self, motivo: str = "Cancelación solicitada") -> None:
        """Cancela una reserva si aún no fue procesada."""
        if self._estado == "PROCESADA":  # Ya cobrada: no se puede cancelar
            raise OperacionReservaError(f"No se puede cancelar la reserva {self.id_entidad}: ya fue PROCESADA.")
        self._estado = "CANCELADA"  # Cambio de estado permitido
        self._motivo_cancelacion = motivo  # Se guarda el motivo
        registrar_log("INFO", f"Reserva {self.id_entidad} cancelada. Motivo: {motivo}")  # Evento relevante

    def procesar(self) -> float:
        """Procesa una reserva confirmada y retorna el monto final."""
        if self._estado != "CONFIRMADA":  # Solo se procesan reservas confirmadas
            raise OperacionReservaError(
                f"Solo se pueden procesar reservas CONFIRMADAS. Estado actual de {self.id_entidad}: {self._estado}."
            )
        try:
            # Se recalcula el total con las condiciones actuales
            nuevo_total = self._servicio.calcular_costo(
                duracion=self._duracion,
                descuento_pct=self._descuento_pct,
                impuesto_pct=self._impuesto_pct,
            )
        except Exception as exc:
            # ENCADENAMIENTO: se conserva el error original como causa (raise ... from ...)
            raise OperacionReservaError(
                f"Fallo al procesar financieramente la reserva {self.id_entidad}."
            ) from exc
        else:
            # try/except/else: este bloque solo corre si el cálculo no falló
            self._total_calculado = nuevo_total  # Se actualiza el total
            self._estado = "PROCESADA"  # Cambio de estado permitido
        finally:
            # try/except/finally: se ejecuta siempre, haya o no error
            registrar_log("AUDITORIA", f"Intento de procesar {self.id_entidad}. Estado resultante: {self._estado}")
        return self._total_calculado

    def resumen(self) -> str:
        """Implementación del método abstracto de la clase base."""
        return str(self)

    def __str__(self) -> str:
        return (
            f"Reserva [{self.id_entidad}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | Duración: {self._duracion} {self._servicio.unidad_tiempo} | "
            f"Total: ${self._total_calculado:,.2f} | Estado: {self._estado}"
        )


class GestorSoftwareFJ:
    """Administra clientes, servicios y reservas en memoria usando listas."""

    def __init__(self) -> None:
        self.clientes: list[Cliente] = []  # Lista interna de clientes
        self.servicios: list[Servicio] = []  # Lista interna de servicios
        self.reservas: list[Reserva] = []  # Lista interna de reservas

    def registrar_cliente(self, cliente: Cliente) -> None:
        # No se permiten IDs de cliente repetidos
        if any(c.id_entidad == cliente.id_entidad for c in self.clientes):
            raise DatoInvalidoError(f"Ya existe un cliente registrado con ID {cliente.id_entidad}.")
        self.clientes.append(cliente)  # Se agrega a la lista

    def registrar_servicio(self, servicio: Servicio) -> None:
        # No se permiten IDs de servicio repetidos
        if any(s.id_entidad == servicio.id_entidad for s in self.servicios):
            raise DatoInvalidoError(f"Ya existe un servicio registrado con ID {servicio.id_entidad}.")
        self.servicios.append(servicio)  # Se agrega a la lista

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        for cliente in self.clientes:  # Recorre la lista de clientes
            if cliente.id_entidad == id_cliente.strip().upper():  # Compara ID normalizado
                return cliente
        raise DatoInvalidoError(f"Cliente con ID '{id_cliente}' no encontrado.")

    def buscar_servicio(self, id_servicio: str) -> Servicio:
        for servicio in self.servicios:  # Recorre la lista de servicios
            if servicio.id_entidad == id_servicio.strip().upper():  # Compara ID normalizado
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
            cliente = self.buscar_cliente(id_cliente)  # Busca el cliente
            servicio = self.buscar_servicio(id_servicio)  # Busca el servicio
            reserva = Reserva(  # Crea la reserva (valida disponibilidad y costos)
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                descuento_pct=descuento_pct,
                impuesto_pct=impuesto_pct,
            )
            self.reservas.append(reserva)  # Solo se agrega a la lista si todo salió bien
            return reserva
        except ErrorSoftwareFJ:
            raise  # Errores propios: se propagan tal cual
        except Exception as exc:
            # ENCADENAMIENTO: un error inesperado (ej. AttributeError) se envuelve conservando su causa
            raise OperacionReservaError(f"Error inesperado al crear la reserva '{id_reserva}'.") from exc


# =====================================================================
# 5. SIMULACIÓN DE OPERACIONES (MÍNIMO 10 OPERACIONES COMPLETAS)
# =====================================================================

def ejecutar_operacion(numero: int, descripcion: str, accion) -> None:
    """
    Ejecuta una operación de simulación usando try / except / else / finally
    para demostrar robustez y registro continuo en logs.
    """
    print(f"\n--- Operación {numero}: {descripcion} ---")  # Encabezado de la operación
    exito = False  # Bandera para el bloque finally
    try:
        resultado = accion()  # Se ejecuta la operación
    except ErrorSoftwareFJ as err_sistema:  # Errores propios del sistema (controlados)
        causa = err_sistema.__cause__  # Causa original si el error fue encadenado
        texto_causa = f" | Causa original: [{type(causa).__name__}] {causa}" if causa else ""
        mensaje = f"Op {numero} ({descripcion}) -> Error controlado [{type(err_sistema).__name__}]: {err_sistema}{texto_causa}"
        print("[ERROR CONTROLADO]", err_sistema)  # Se informa en pantalla
        if causa:  # Si hubo encadenamiento, también se muestra la causa
            print(f"   ↳ Causa encadenada: [{type(causa).__name__}] {causa}")
        registrar_log("ERROR", mensaje)  # Se registra en el log
    except Exception as err_general:  # Cualquier otro error no previsto
        try:
            # Se envuelve el error en una excepción propia, encadenando la causa
            raise OperacionReservaError(f"Fallo no previsto en Op {numero}") from err_general
        except OperacionReservaError as envuelta:
            mensaje = (
                f"Op {numero} ({descripcion}) -> Excepción encadenada [{type(envuelta).__name__}]: "
                f"{envuelta} | Causa: [{type(err_general).__name__}] {err_general}"
            )
            print("[EXCEPCIÓN ENCADENADA]", mensaje)  # Se informa en pantalla
            registrar_log("CRITICAL", mensaje)  # Se registra en el log
    else:
        exito = True  # Solo llega aquí si no hubo ninguna excepción
        detalle = resultado if resultado is not None else "Completada sin errores."
        print("[ÉXITO]", detalle)  # Se informa en pantalla
        registrar_log("INFO", f"Op {numero} ({descripcion}) -> {detalle}")  # Se registra en el log
    finally:
        # Este bloque se ejecuta siempre: así cada operación queda auditada
        estado_final = "OK" if exito else "CON_ERROR_MANEJADO"
        registrar_log("AUDITORIA", f"Fin de Operación {numero} | Estado: {estado_final}")


def simular_sistema_software_fj() -> None:
    """Ejecuta 15 operaciones variadas para probar el sistema completo."""
    gestor = GestorSoftwareFJ()  # Gestor con las listas en memoria
    registrar_log("INFO", "Inicio de simulación del sistema Software FJ.")

    def op1():
        c1 = Cliente("CLI-01", "Cristian Majin", "cristian@example.com", "3105551234")
        gestor.registrar_cliente(c1)
        return c1.resumen()

    def op2():
        c_malo = Cliente("CLI-02", "Ana", "correo_sin_arroba", "123")  # Correo inválido
        gestor.registrar_cliente(c_malo)
        return c_malo.resumen()

    def op3():
        c2 = Cliente("CLI-03", "Dali Velasco", "dali@example.com", "3159876543")
        gestor.registrar_cliente(c2)
        return c2.resumen()

    def op4():
        s1 = ReservaSala("SRV-SALA1", "Sala de Conferencias A", 80000, capacidad_personas=20, disponible=True)
        gestor.registrar_servicio(s1)
        return s1.resumen()

    def op5():
        s2 = AlquilerEquipo("SRV-EQ1", "Portátil Empresarial i7", 45000, "Laptop", disponible=True)
        # Esta asesoría se crea NO disponible a propósito, para probar la Operación 9
        s3 = AsesoriaEspecializada("SRV-ASE1", "Arquitectura Python y POO", 120000, "Backend & POO", disponible=False)
        gestor.registrar_servicio(s2)
        gestor.registrar_servicio(s3)
        return f"Registrados: {s2.id_entidad} y {s3.id_entidad} (no disponible a propósito)"

    def op6():
        s_malo = ReservaSala("SRV-ERR", "Sala Inválida", -5000, capacidad_personas=10)  # Tarifa negativa
        gestor.registrar_servicio(s_malo)
        return s_malo.resumen()

    def op7():
        res1 = gestor.crear_reserva("RES-001", "CLI-01", "SRV-SALA1", duracion=3, descuento_pct=10, impuesto_pct=19)
        res1.confirmar()
        total_cobrado = res1.procesar()
        return f"{res1} | Cobrado: ${total_cobrado:,.2f}"

    def op8():
        res2 = gestor.crear_reserva("RES-002", "CLI-03", "SRV-EQ1", duracion=6)  # Descuento e IVA por defecto
        res2.confirmar()
        return f"{res2} (queda confirmada, aún sin procesar)"

    def op9():
        return str(gestor.crear_reserva("RES-003", "CLI-01", "SRV-ASE1", duracion=2))  # Servicio no disponible

    def op10():
        return str(gestor.crear_reserva("RES-004", "CLI-01", "SRV-SALA1", duracion=20))  # Más de 12 horas

    def op11():
        res_temp = gestor.crear_reserva("RES-005", "CLI-03", "SRV-EQ1", duracion=2)
        res_temp.cancelar("Cambio de agenda")  # Se cancela correctamente (queda en el log)
        return str(res_temp.procesar())  # Procesar una reserva cancelada debe fallar

    def op12():
        return str(gestor.crear_reserva("RES-006", "CLI-999", "SRV-EQ1", duracion=1))  # Cliente inexistente

    def op13():
        res = gestor.crear_reserva("RES-007", "CLI-01", "SRV-SALA1", duracion=2)
        res.confirmar()
        res.ajustar_condiciones(descuento_pct=150)  # Descuento imposible (>100%)
        return str(res.procesar())  # Falla y encadena CalculoFinancieroError como causa

    def op14():
        # id_cliente=None provoca un AttributeError interno que se encadena en OperacionReservaError
        return str(gestor.crear_reserva("RES-008", None, "SRV-EQ1", duracion=1))

    def op15():
        sala = gestor.buscar_servicio("SRV-SALA1")
        base = sala.calcular_costo(2)  # Variante 1: solo duración
        con_iva = sala.calcular_costo_con_impuesto(2, 19)  # Variante 2: con impuesto
        con_desc = sala.calcular_costo_con_descuento(2, 10)  # Variante 3: con descuento
        completo = sala.calcular_costo(2, descuento_pct=5, impuesto_pct=19, cargo_adicional=20000)  # Variante 4
        return (
            f"Sala 2h -> base: ${base:,.2f} | con IVA 19%: ${con_iva:,.2f} | "
            f"con descuento 10%: ${con_desc:,.2f} | completo: ${completo:,.2f}"
        )

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
        (13, "Procesamiento fallido con encadenamiento de excepciones", op13),
        (14, "Error inesperado encadenado al crear reserva", op14),
        (15, "Cálculo de costos con variantes sobrecargadas", op15),
    ]

    for num, desc, fn in operaciones:  # Ejecuta cada operación; un error nunca detiene el ciclo
        ejecutar_operacion(num, desc, fn)

    print("\n=== RESUMEN FINAL EN MEMORIA ===")
    print(f"Clientes registrados: {len(gestor.clientes)}")
    print(f"Servicios registrados: {len(gestor.servicios)}")
    print(f"Reservas creadas: {len(gestor.reservas)}")
    for r in gestor.reservas:  # Lista cada reserva que quedó en memoria
        print("  *", r)

    registrar_log("INFO", "Fin de simulación del sistema Software FJ.")
    if os.path.exists(ARCHIVO_LOG):  # Confirma que el log fue generado
        print(f"\nArchivo de logs generado: '{ARCHIVO_LOG}'")


if __name__ == "__main__":
    simular_sistema_software_fj()  # Punto de entrada del programa
