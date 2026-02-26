import os

class Config:
    SECRET_KEY = 'tu-clave-secreta-aqui-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///nomina.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración del lector biométrico ZKTeco
    ZKTECO_IP = '192.168.1.201'  # Cambia esto por la IP de tu lector
    ZKTECO_PORT = 4370           # Puerto por defecto de ZKTeco