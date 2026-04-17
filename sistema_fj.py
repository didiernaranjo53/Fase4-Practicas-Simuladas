import logging
from abc import ABC, abstractmethod

# ==========================================
# CONFIGURACION: LOGS
# ==========================================
logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==========================================
# 1. EXCEPCIONES PERSONALIZADAS
# ==========================================
class ValidationError(Exception): pass
class ReservaError(Exception): pass
class OperacionNoPermitidaError(Exception): pass

# ==========================================
# 2. CLASE ABSTRACTA: ENTIDAD
# ==========================================
class Entidad(ABC):
    @abstractmethod
    def obtener_detalles(self):
        pass

# ==========================================
# 3. CLASE: CLIENTE (Encapsulamiento Robusto)
# ==========================================
class Cliente(Entidad):
    def __init__(self, identificacion, nombre, email):
        self.identificacion = identificacion
        self.nombre = nombre
        self.email = email

    @property
    def identificacion(self): return self._identificacion

    @identificacion.setter
    def identificacion(self, valor):
        if not valor or not isinstance(valor, str):
            raise ValidationError("Validacion: La identificacion debe ser texto.")
        self._identificacion = valor
        
    @property
    def nombre(self): return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if len(valor) < 3:
            raise ValidationError("Validacion: El nombre debe tener al menos 3 letras.")
        self._nombre = valor
        
    @property
    def email(self): return self._email

    @email.setter
    def email(self, valor):
        if "@" not in valor:
            raise ValidationError("Validacion: El correo es invalido (falta '@').")
        self._email = valor

    def obtener_detalles(self):
        return f"Cliente: {self.nombre} (ID: {self.identificacion})"

# ==========================================
# 4. CAPA DE SERVICIOS (Polimorfismo)
# ==========================================
class Servicio(Entidad):
    def __init__(self, nombre_servicio, tarifa_base):
        self.nombre_servicio = nombre_servicio
        self.tarifa_base = tarifa_base
        
    @abstractmethod
    def calcular_costo_final(self, tiempo, impuesto=0.0, descuento=0.0):
        # Parametros obligatorios y opcionales para emular sobrecarga
        pass

class ReservaDeSala(Servicio):
    def calcular_costo_final(self, horas, impuesto=0.0, descuento=0.0):
        try:
            if horas <= 0:
                raise ValueError("Las horas de reserva no pueden ser cero ni negativas.")
            subtotal = self.tarifa_base * horas
            total = subtotal + (subtotal * impuesto) - descuento
            if total < 0:
                raise OperacionNoPermitidaError("Costo negativo por exceso de descuento.")
            return total
        except ValueError as e:
            # Excepcion encadenada
            raise ReservaError("Fallo grave al calcular Reserva de la Sala.") from e
            
    def obtener_detalles(self):
        return f"Sala: {self.nombre_servicio} [Tarifa/Hr: ${self.tarifa_base}]"

class AlquilerEquipos(Servicio):
    def calcular_costo_final(self, dias, impuesto=0.0, descuento=0.0):
        subtotal = self.tarifa_base * dias
        return max(subtotal + (subtotal * impuesto) - descuento, 0)
        
    def obtener_detalles(self):
        return f"Equipos: {self.nombre_servicio} [Tarifa/Dia: ${self.tarifa_base}]"

class AsesoriaEspecializada(Servicio):
    def calcular_costo_final(self, sesiones, impuesto=0.0, descuento=0.0):
        subtotal = (self.tarifa_base * sesiones) + 50 # Fee tecnico fijo
        return subtotal + (subtotal * impuesto) - descuento
        
    def obtener_detalles(self):
        return f"Asesoria Tecnica: {self.nombre_servicio} [Tarifa/Sesion: ${self.tarifa_base} + Fee $50]"

# ==========================================
# 5. GESTOR DE RESERVAS (Manejo con try/except/else/finally)
# ==========================================
class Reserva:
    def __init__(self, cliente, servicio, cantidad_tiempo):
        if not isinstance(cliente, Cliente):
            raise ValidationError("Objeto Cliente invalido en la Reserva.")
        if not isinstance(servicio, Servicio):
            raise ValidationError("Objeto Servicio invalido en la Reserva.")
            
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad_tiempo = cantidad_tiempo
        self.estado = "PENDIENTE"
        logging.info(f"Intencion de reserva PENDIENTE para {cliente.nombre}.")

    def procesar_reserva(self, impuesto=0.0, descuento=0.0):
        logging.info("Procesando reserva...")
        costo_final = 0
        try:
            costo_final = self.servicio.calcular_costo_final(self.cantidad_tiempo, impuesto, descuento)
            
        except ReservaError as re:
            self.estado = "FALLIDA"
            logging.error(f"[ERROR MANEJADO] Problema en calculo: {re} - Causa: {re.__cause__}")
            raise
            
        except Exception as e:
            self.estado = "ERROR CRITICO"
            logging.critical(f"[FALLO INESPERADO] Excepcion general: {e}")
            raise
            
        else:
            self.estado = "CONFIRMADA EXITOSAMENTE"
            resumen = f"EXITO: Resumen | {self.cliente.nombre} | {self.servicio.nombre_servicio} | Total: ${costo_final:.2f}"
            logging.info(resumen)
            return resumen
            
        finally:
            estado_log = f"--- Estado final Reserva ({self.cliente.nombre}): {self.estado} --- \n"
            logging.info(estado_log)

# ==========================================
# 6. MODULO DE SIMULACION Y MENU
# ==========================================
def simular_10_operaciones():
    print("\n--- INICIANDO DIAGNOSTICO AUTOMATICO DE ROBUSTEZ ---")
    logging.info("=========== NUEVA SESION DE PRUEBAS AUTOMATICAS ===========")
    
    # Base de servicios
    s_auditorio = ReservaDeSala("Auditorio", 150)
    s_redes = AlquilerEquipos("Routers Cisco", 200)
    s_seguridad = AsesoriaEspecializada("Pentesting", 400)
    operaciones = 0

    def ejecutor(titulo, func):
        nonlocal operaciones
        operaciones += 1
        print(f"\nOp {operaciones}: {titulo}")
        try:
            func()
        except ValidationError as ve:
            print(f"[X] ValidationError capturado a salvo -> {ve}")
            logging.warning(f"Simulacion Op{operaciones}: {ve}")
        except ReservaError as re:
            print(f"[X] ReservaError capturado a salvo -> {re}")
            logging.error(f"Simulacion Op{operaciones}: {re}")
        except Exception as e:
            print(f"[X] Exception general evitada -> {e}")
            logging.error(f"Simulacion Op{operaciones} Exception: {e}")

    # 1 al 10: Registros Validos/Invalidos, Reservas, Excepciones
    ejecutor("Cliente Válido", lambda: print(Cliente("1", "Empresa A", "a@a.com").obtener_detalles()))
    ejecutor("Cliente Inválido (Correo malo)", lambda: Cliente("2", "Pepe", "correo_malo.com"))
    ejecutor("Cliente Inválido (Nombre corto)", lambda: Cliente("3", "A", "a@a.com"))
    
    def op_4():
        c = Cliente("4", "Soluciones IT", "it@soluciones.com")
        res = Reserva(c, s_seguridad, 3)
        print(res.procesar_reserva(impuesto=0.15)) # Sobrecarga
    ejecutor("Reserva Válida (Asesoria + Impuestos)", op_4)
    
    def op_5():
        c = Cliente("5", "Fallos Corp", "f@f.com")
        res = Reserva(c, s_auditorio, -5) # Horas negativas causa ReservaError
        res.procesar_reserva()
    ejecutor("Reserva Inválida (Horas negativas en Sala)", op_5)
    
    def op_6():
        c = Cliente("6", "Error Tech", "e@tech.com")
        res = Reserva(c, s_auditorio, 2)
        print(res.procesar_reserva(descuento=5000)) # Descuento enorme causa error
    ejecutor("Reserva Inválida (Valores resultan negativos)", op_6)
    
    def op_7():
        c = Cliente("7", "Valid Corp", "v@v.com")
        res = Reserva("NoSoyObjetoCliente", s_redes, 5) # Mal Inyeccion dependencias
    ejecutor("Reserva Inicializacion Inválida (Cliente erroneo)", op_7)
    
    def op_8():
        servicios = [s_auditorio, s_redes, s_seguridad]
        for s in servicios: print("Polimorfismo:", s.obtener_detalles())
    ejecutor("Demostración de Polimorfismo exitoso", op_8)
    
    def op_9():
        c = Cliente("9", "Crash Test", "c@dummy.com")
        res = Reserva(c, s_redes, "Cinco") # Multiplicar string por flotante rompe python nativo
        res.procesar_reserva()
    ejecutor("Error Critico tipo nativo de Python capturado", op_9)
    
    def op_10():
        c = Cliente("10", "Fin Prueba", "fin@prueba.com")
        res = Reserva(c, s_auditorio, 10)
        print(res.procesar_reserva())
    ejecutor("La app SIEMPRE termina viva (Prueba 10 exitosa)", op_10)
    print("\n--- SIMULACION COMPLETADA: LA APP NUNCA SE CERRO POR ERROR ---")


def menu_interactivo():
    while True:
        print("\n=== SOFTWARE FJ - SISTEMA DE GESTION (POO) ===")
        print("1. Ejecutar Simulacion Calificable (10 Operaciones Robustas)")
        print("2. Registrar Cliente Manual (Jugar con Validaciones)")
        print("3. Salir")
        opcion = input("Selecciona una opcion: ")
        
        if opcion == "1":
            simular_10_operaciones()
        elif opcion == "2":
            print("\n-- Registro de Nuevo Cliente --")
            id_cli = input("Ingresa ID: ")
            nom_cli = input("Ingresa Nombre (min 3 letras): ")
            mail_cli = input("Ingresa Correo (con @): ")
            try:
                nuevo = Cliente(id_cli, nom_cli, mail_cli)
                logging.info(f"[Registro Manual] Nuevo cliente creado: {nuevo.nombre}")
                print(f"[EXITO] -> {nuevo.obtener_detalles()}")
            except ValidationError as ve:
                logging.warning(f"[Registro Manual Fallido]: {ve}")
                print(f"[ERROR CAPTURADO] El cliente no se creo porque: {ve}")
        elif opcion == "3":
            print("Saliendo del sistema...")
            break
        else:
            print("Opcion invalida.")

if __name__ == "__main__":
    menu_interactivo()
