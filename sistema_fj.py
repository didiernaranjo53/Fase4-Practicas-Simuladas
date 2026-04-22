import logging
from abc import ABC, abstractmethod

# ==========================================
# CONFIGURACION DE LOGS
# ==========================================
logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# ==========================================
# EXCEPCIONES PERSONALIZADAS
# ==========================================
class ValidationError(Exception):
    pass

class ReservaError(Exception):
    pass

class OperacionNoPermitidaError(Exception):
    pass


# ==========================================
# CLASE ABSTRACTA BASE
# ==========================================
class Entidad(ABC):
    @abstractmethod
    def obtener_detalles(self):
        pass

# ==========================================
# CLASE CLIENTE
# ==========================================
class Cliente(Entidad):
    def __init__(self, identificacion, nombre, email):
        self.identificacion = identificacion
        self.nombre = nombre
        self.email = email

    @property
    def identificacion(self):
        return self._identificacion

    @identificacion.setter
    def identificacion(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValidationError("La identificación debe ser texto válido.")
        self._identificacion = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if len(valor.strip()) < 3:
            raise ValidationError("El nombre debe tener mínimo 3 caracteres.")
        self._nombre = valor

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if "@" not in valor:
            raise ValidationError("Correo electrónico inválido.")
        self._email = valor

    def obtener_detalles(self):
        return f"Cliente: {self.nombre} | ID: {self.identificacion} | Email: {self.email}"


# ==========================================
# CLASE ABSTRACTA SERVICIO
# ==========================================
class Servicio(Entidad):
    def __init__(self, nombre_servicio, tarifa_base):
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = tarifa_base

    @abstractmethod
    def calcular_costo_final(self, tiempo, impuesto=0, descuento=0):
        pass


# ==========================================
# SERVICIOS ESPECIALIZADOS
# ==========================================
class ReservaSala(Servicio):
    def calcular_costo_final(self, horas, impuesto=0, descuento=0):
        try:
            if horas <= 0:
                raise ValueError("Las horas deben ser mayores a cero.")

            subtotal = self.tarifa_base * horas
            total = subtotal + subtotal * impuesto - descuento

            if total < 0:
                raise OperacionNoPermitidaError("El costo no puede ser negativo.")

            return total

        except ValueError as e:
            raise ReservaError("Error en reserva de sala.") from e

    def obtener_detalles(self):
        return f"Reserva Sala: {self.nombre_servicio} - ${self.tarifa_base}/hora"


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


class AsesoriaEspecializada(Servicio):
    def calcular_costo_final(self, sesiones, impuesto=0, descuento=0):
        if sesiones <= 0:
            raise ReservaError("Las sesiones deben ser mayores a cero.")

        subtotal = (self.tarifa_base * sesiones) + 50
        total = subtotal + subtotal * impuesto - descuento

        if total < 0:
            raise OperacionNoPermitidaError("Costo inválido.")

        return total

    def obtener_detalles(self):
        return f"Asesoría: {self.nombre_servicio} - ${self.tarifa_base}/sesión + $50 fijo"

# ==========================================
# CLASE RESERVA
# ==========================================
class Reserva:
    def __init__(self, cliente, servicio, cantidad):
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
            costo = self.servicio.calcular_costo_final(
                self.cantidad,
                impuesto,
                descuento
            )

        except Exception as e:
            self.estado = "FALLIDA"
            logging.error(f"Error al procesar reserva: {e}")
            raise

        else:
            self.estado = "CONFIRMADA"
            logging.info(f"Reserva confirmada para {self.cliente.nombre}")
            return costo

        finally:
            logging.info(f"Estado final reserva: {self.estado}")

    def obtener_detalles(self):
        return f"{self.cliente.nombre} | {self.servicio.nombre_servicio} | Estado: {self.estado}"

# ==========================================
# SISTEMA PRINCIPAL
# ==========================================
class SistemaGestion:
    def __init__(self):
        self.clientes = []
        self.reservas = []
        self.servicios = [
            ReservaSala("Sala de Juntas", 100),
            AlquilerEquipo("Portátil", 80),
            AsesoriaEspecializada("Seguridad Informática", 200)
        ]

    def registrar_cliente(self, identificacion, nombre, email):
        if any(c.identificacion == identificacion for c in self.clientes):
            raise ValidationError("Ya existe un cliente con ese ID.")

        cliente = Cliente(identificacion, nombre, email)
        self.clientes.append(cliente)
        logging.info(f"Cliente registrado: {cliente.nombre}")
        return cliente

    def buscar_cliente(self, identificacion):
        for cliente in self.clientes:
            if cliente.identificacion == identificacion:
                return cliente
        raise ValidationError("Cliente no encontrado.")

    def crear_reserva(self, identificacion_cliente, indice_servicio, cantidad):
        cliente = self.buscar_cliente(identificacion_cliente)

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

# ==========================================
# SIMULACION DE 10 OPERACIONES
# ==========================================
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

# ==========================================
# MENU
# ==========================================
def menu():
    sistema = SistemaGestion()

    while True:
        print("\n===== SOFTWARE FJ =====")
        print("1. Registrar cliente")
        print("2. Crear reserva")
        print("3. Listar clientes")
        print("4. Listar reservas")
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

# ==========================================
# EJECUCION
# ==========================================
if __name__ == "__main__":
    menu()
