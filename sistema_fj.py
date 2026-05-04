import logging
from abc import ABC, abstractmethod

# =====================================================
# CONFIGURACIÓN DEL SISTEMA DE LOGS
# =====================================================
# Se crea un archivo llamado logs.txt donde se almacenarán
# eventos importantes del sistema como registros, errores
# y confirmaciones de reservas.
logging.basicConfig(
    filename='logs.txt',                  # Archivo donde se guardan logs
    level=logging.INFO,                   # Nivel mínimo de mensajes a registrar
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato del mensaje
)

# =====================================================
# EXCEPCIONES PERSONALIZADAS
# =====================================================
# Se crean excepciones propias para controlar errores
# específicos del sistema y hacer el código más organizado.
class ValidationError(Exception):
    pass  # Error para validaciones incorrectas

class ReservaError(Exception):
    pass  # Error relacionado con reservas

class OperacionNoPermitidaError(Exception):
    pass  # Error cuando una operación genera datos inválidos


# =====================================================
# CLASE ABSTRACTA BASE
# =====================================================
# Clase padre para obligar a que todas las entidades
# implementen el método obtener_detalles()
class Entidad(ABC):

    @abstractmethod
    def obtener_detalles(self):
        pass


# =====================================================
# CLASE CLIENTE
# =====================================================
# Representa a un cliente del sistema
class Cliente(Entidad):

    def __init__(self, identificacion, nombre, email):
        # Se asignan atributos usando setters para validar datos
        self.identificacion = identificacion
        self.nombre = nombre
        self.email = email

    # ---------- VALIDACIÓN IDENTIFICACIÓN ----------
    @property
    def identificacion(self):
        return self._identificacion

    @identificacion.setter
    def identificacion(self, valor):
        # Debe ser texto y no estar vacío
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("Identificación debe ser texto válido.")
        self._identificacion = valor

    # ---------- VALIDACIÓN NOMBRE ----------
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        # Mínimo 3 caracteres
        if len(valor.strip()) < 3:
            raise ValidationError("Nombre debe tener mínimo 3 caracteres.")
        self._nombre = valor

    # ---------- VALIDACIÓN EMAIL ----------
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        # Validación básica: debe contener @
        if "@" not in valor:
            raise ValidationError("Correo electrónico no válido.")
        self._email = valor

    # Método obligatorio heredado de Entidad
    def obtener_detalles(self):
        return f"Cliente: {self.nombre} | ID: {self.identificacion} | Email: {self.email}"


# =====================================================
# CLASE ABSTRACTA SERVICIO
# =====================================================
# Define estructura base para todos los servicios
class Servicio(Entidad):

    def __init__(self, nombre_servicio, tarifa_base):
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = tarifa_base

    @abstractmethod
    def calcular_costo_final(self, tiempo, impuesto=0, descuento=0):
        pass


# =====================================================
# SERVICIO: RESERVA DE SALAS
# =====================================================
class ReservaSala(Servicio):

    def calcular_costo_final(self, horas, impuesto=0, descuento=0):
        try:
            # Validar horas positivas
            if horas <= 0:
                raise ValueError("Las horas deben ser mayores a cero.")

            # Cálculo subtotal
            subtotal = self.tarifa_base * horas

            # Aplicación de impuesto y descuento
            total = subtotal + subtotal * impuesto - descuento

            # No permitir costos negativos
            if total < 0:
                raise OperacionNoPermitidaError("El costo no puede ser negativo.")

            return total

        except ValueError as e:
            raise ReservaError("Error en la reserva de sala.") from e

    def obtener_detalles(self):
        return f"Reserva Sala: {self.nombre_servicio} - ${self.tarifa_base}/hora"


# =====================================================
# SERVICIO: ALQUILER DE EQUIPOS
# =====================================================
class AlquilerEquipo(Servicio):

    def calcular_costo_final(self, dias, impuesto=0, descuento=0):
        if dias <= 0:
            raise ReservaError("Los días deben ser mayores a cero.")

        subtotal = self.tarifa_base * dias
        total = subtotal + subtotal * impuesto - descuento

        if total < 0:
            raise OperacionNoPermitidaError("Costo inválido.")

        return total

    def obtener_detalles(self):
        return f"Alquiler Equipo: {self.nombre_servicio} - ${self.tarifa_base}/día"


# =====================================================
# SERVICIO: ASESORÍA ESPECIALIZADA
# =====================================================
class AsesoriaEspecializada(Servicio):

    def calcular_costo_final(self, sesiones, impuesto=0, descuento=0):
        if sesiones <= 0:
            raise ReservaError("Las sesiones deben ser mayores a cero.")

        # Tiene costo fijo adicional de 50
        subtotal = (self.tarifa_base * sesiones) + 50
        total = subtotal + subtotal * impuesto - descuento

        if total < 0:
            raise OperacionNoPermitidaError("Costo inválido.")

        return total

    def obtener_detalles(self):
        return f"Asesoría: {self.nombre_servicio} - ${self.tarifa_base}/sesión + $50 fijo"


# =====================================================
# CLASE RESERVA
# =====================================================
# Relaciona cliente + servicio + cantidad
class Reserva:

    def __init__(self, cliente, servicio, cantidad):
        # Validar tipos de datos
        if not isinstance(cliente, Cliente):
            raise ValidationError("Cliente inválido.")
        if not isinstance(servicio, Servicio):
            raise ValidationError("Servicio inválido.")

        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "PENDIENTE"

    def procesar_reserva(self, impuesto=0, descuento=0):
        try:
            # Calcula costo final usando polimorfismo
            costo = self.servicio.calcular_costo_final(
                self.cantidad,
                impuesto,
                descuento
            )

        except Exception as e:
            # Si falla cambia estado y registra error
            self.estado = "FALLIDA"
            logging.error(f"Error al procesar reserva: {e}")
            raise

        else:
            # Si todo sale bien
            self.estado = "CONFIRMADA"
            logging.info(f"Reserva confirmada para {self.cliente.nombre}")
            return costo

        finally:
            # Siempre registra estado final
            logging.info(f"Estado final reserva: {self.estado}")

    def obtener_detalles(self):
        return f"{self.cliente.nombre} | {self.servicio.nombre_servicio} | Estado: {self.estado}"


# =====================================================
# SISTEMA PRINCIPAL DE GESTIÓN
# =====================================================
class SistemaGestion:

    def __init__(self):
        self.clientes = []
        self.reservas = []

        # Servicios disponibles del sistema
        self.servicios = [
            ReservaSala("Sala de Juntas", 100),
            AlquilerEquipo("Portátil", 80),
            AsesoriaEspecializada("Seguridad Informática", 200)
        ]

    def registrar_cliente(self, identificacion, nombre, email):
        # Verifica que no exista cliente repetido
        if any(c.identificacion == identificacion for c in self.clientes):
            raise ValidationError("Ya existe un cliente con ese ID.")

        cliente = Cliente(identificacion, nombre, email)
        self.clientes.append(cliente)

        logging.info(f"Cliente registrado: {cliente.nombre}")
        return cliente

    def buscar_cliente(self, identificacion):
        # Busca cliente por ID
        for cliente in self.clientes:
            if cliente.identificacion == identificacion:
                return cliente
        raise ValidationError("Cliente no encontrado.")

    def crear_reserva(self, identificacion_cliente, indice_servicio, cantidad):
        cliente = self.buscar_cliente(identificacion_cliente)

        # Validar índice de servicio
        if indice_servicio < 0 or indice_servicio >= len(self.servicios):
            raise ValidationError("Servicio inválido.")

        servicio = self.servicios[indice_servicio]

        reserva = Reserva(cliente, servicio, cantidad)
        costo = reserva.procesar_reserva()

        self.reservas.append(reserva)

        return reserva, costo

    def listar_clientes(self):
        for cliente in self.clientes:
            print(cliente.obtener_detalles())

    def listar_reservas(self):
        for reserva in self.reservas:
            print(reserva.obtener_detalles())


# =====================================================
# SIMULACIÓN DE PRUEBAS AUTOMÁTICAS
# =====================================================
# Ejecuta 10 operaciones válidas e inválidas para probar
# manejo de errores y funcionamiento general.
def simulacion():
    sistema = SistemaGestion()

    pruebas = [
        lambda: sistema.registrar_cliente("1", "Carlos Perez", "carlos@mail.com"),
        lambda: sistema.registrar_cliente("2", "Ana", "ana@mail.com"),
        lambda: sistema.registrar_cliente("1", "Duplicado", "dup@mail.com"),
        lambda: sistema.registrar_cliente("3", "Lu", "lu@mail.com"),
        lambda: sistema.registrar_cliente("4", "Maria Lopez", "maria.com"),
        lambda: sistema.crear_reserva("1", 0, 3),
        lambda: sistema.crear_reserva("2", 1, 2),
        lambda: sistema.crear_reserva("1", 0, -5),
        lambda: sistema.crear_reserva("9", 1, 2),
        lambda: sistema.crear_reserva("2", 5, 1)
    ]

    for i, prueba in enumerate(pruebas, start=1):
        try:
            print(f"\nOperación {i}")
            resultado = prueba()
            print("Éxito:", resultado)
        except Exception as e:
            print("Error controlado:", e)


# =====================================================
# MENÚ INTERACTIVO
# =====================================================
def menu():
    sistema = SistemaGestion()

    while True:
        print("\n===== SOFTWARE FJ =====")
        print("1. Registrar cliente")
        print("2. Crear una reserva")
        print("3. Listar los clientes")
        print("4. Listar las reservas")
        print("5. Ejecutar simulación")
        print("6. Salir")

        opcion = input("Seleccione opción: ")

        try:
            if opcion == "1":
                idc = input("ID: ")
                nom = input("Nombre: ")
                mail = input("Email: ")

                sistema.registrar_cliente(idc, nom, mail)
                print("Cliente registrado correctamente.")

            elif opcion == "2":
                idc = input("ID cliente: ")

                # Mostrar servicios disponibles
                for i, servicio in enumerate(sistema.servicios):
                    print(i, "-", servicio.obtener_detalles())

                indice = int(input("Servicio: "))
                cantidad = int(input("Cantidad tiempo: "))

                reserva, costo = sistema.crear_reserva(idc, indice, cantidad)
                print(f"Reserva exitosa. Total: ${costo}")

            elif opcion == "3":
                sistema.listar_clientes()

            elif opcion == "4":
                sistema.listar_reservas()

            elif opcion == "5":
                simulacion()

            elif opcion == "6":
                print("Saliendo del sistema...")
                break

            else:
                print("Opción inválida.")

        except Exception as e:
            print("Error:", e)


# =====================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# =====================================================
# Solo ejecuta menú si el archivo se corre directamente
if __name__ == "__main__":
    menu()
