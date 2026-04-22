# 🏢 Software FJ - Sistema de Gestión

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![OOP](https://img.shields.io/badge/OOP-Paradigm-brightgreen?style=for-the-badge)

Sistema Integral Orientado a Objetos para la gestión de clientes, servicios y reservas. Desarrollado como parte de la **Fase 4 - Componente Práctico** de la UNAD.

## 🎯 Objetivo general del Proyecto
Diseñar un sistema orientado a objetivos para la gestion de clientes, servicios y reservas de la empresa Software FJ, Contribuyendo con principios solidos de programacion y el manejo avanzado de excepciones, manteniendo estabilidad, modularidad sin hacer uso de base de datos
## 🎯 Objetivos especificos
Hacer uso en la programacion de abstraccion, encapsulados, herencia y polimorfismo.
Diseñar un sistema de reservas
ejecutar métodos de sobrecarga para calculos rapidos de costos
Evidenciar eventos y errores de los logs

## 🧩 Arquitectura del Sistema
El proyecto se basa en una arquitectura de scripts unificados divididos en capas lógicas:

1. **Excepciones Personalizadas (`CustomExceptions`)**: Jerarquía de errores para procesar fallos lógicos específicos.
2. **Capa `Entidad` y `Cliente`**: Estricto uso de *Getters* y *Setters* para validar datos inmutables.
3. **Capa `Servicios`**: Implementación de polimorfismo a través del cálculo de tarifas dependientes del tipo de servicio (Salas, Equipos, Asesorías).
4. **Reserva Gestor**: Motor central que procesa la operación demostrando sobrecarga de métodos calculando impuestos y recargos opcionales sin romper por falta de argumentos.

## 🛠️ Simulación de Entorno
El código incluye un bloque principal `__main__` que dispara 10 simulaciones consecutivas inyectando fallos catastróficos, desbordes de memoria o datos nulos (por ejemplo, correos sin formato o valores negativos en tiempo). El manejo encapsulado previene el *crash* del sistema operativo y en su lugar emite diagnósticos a una traza de historial inmutable (`logs.txt`).

## 🚀 Ejecución
Para visualizar la auditoría de ejecución local:
```bash
python sistema_fj.py
```
> Todos los reportes críticos o advertencias de validación se generarán en el archivo de texto `logs.txt` anexo en la misma ruta de la aplicación.
