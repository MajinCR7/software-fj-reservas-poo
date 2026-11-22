# Software FJ - Sistema de Gestión de Clientes, Servicios y Reservas

Curso: Programación (213023) - Universidad Nacional Abierta y-a Distancia (UNAD)

Fase 4 - Componente práctico - Prácticas simuladas

## Integrantes del grupo
- Cristian Majin
- [Nombre integrante 2]
- [Nombre integrante 3]
- [Nombre integrante 4]
- [Nombre integrante 5]

## Descripción
Sistema orientado a objetos en Python para la empresa Software FJ. Gestiona clientes, servicios (salas, equipos y asesorías) y reservas, sin base de datos: todo se maneja con objetos y listas en memoria. Los eventos y errores se registran en un archivo de logs, y el programa sigue funcionando aunque ocurran errores.

## Archivos del repositorio
- sistema_software_fj.py: código fuente completo, comentado.
- practica_fase4_software_fj.ipynb: notebook de Colab que descarga y ejecuta el sistema y muestra el log.
- logs_software_fj.txt: log generado por una ejecución de la simulación.

## Estructura de clases
- EntidadSistema (abstracta): clase base con ID de entidad.
- Cliente: datos personales encapsulados y validados (nombre, correo, teléfono).
- Servicio (abstracta): define validar_parametros, calcular_costo_base y describir_servicio.
  - ReservaSala: se reserva por horas (1 a 12).
  - AlquilerEquipo: se alquila por días (1 a 30), con descuento del 5% si pasa de 5 días.
  - AsesoriaEspecializada: sesiones por horas (1 a 8).
- Reserva: integra cliente, servicio, duración y estado (PENDIENTE, CONFIRMADA, PROCESADA, CANCELADA).
- GestorSoftwareFJ: administra las listas de clientes, servicios y reservas.

## Conceptos aplicados
- Abstracción, herencia, polimorfismo y encapsulación.
- Sobrecarga mediante parámetros opcionales (calcular_costo con descuento, impuesto y cargo adicional) y variantes calcular_costo_con_impuesto y calcular_costo_con_descuento.
- Excepciones personalizadas: ErrorSoftwareFJ, DatoInvalidoError, ServicioNoDisponibleError, OperacionReservaError y CalculoFinancieroError.
- Bloques try/except, try/except/else y try/except/finally.
- Encadenamiento de excepciones con raise ... from (operaciones 13 y 14 de la simulación).
- Registro de eventos y errores en archivo de logs.

## Simulación
El programa ejecuta 15 operaciones: registros válidos e inválidos de clientes, creación correcta e incorrecta de servicios, reservas exitosas y fallidas, y cálculo de costos con variantes. Los IDs de los ejemplos se asignan a mano en cada operación, por eso hay saltos en la numeración (por ejemplo CLI-01 y CLI-03).

## Cómo ejecutarlo
Opción 1 (Colab): abrir practica_fase4_software_fj.ipynb con el botón "Open in Colab" y ejecutar todas las celdas.

Opción 2 (local): tener Python 3.9 o superior y ejecutar en la terminal: python sistema_software_fj.py
El archivo logs_software_fj.txt se genera en la misma carpeta.
