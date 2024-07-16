import json
from typing import Dict, Any

def load_config(file_path: str = 'assets/config.json') -> Dict[str, Any]:
    
    """
    Carga la configuración desde un archivo JSON.
    
    :param file_path: Ruta al archivo de configuración JSON
    :return: Diccionario con la configuración cargada
    """
    try:
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Error: El archivo de configuración '{file_path}' no se encontró.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: El archivo '{file_path}' no contiene un JSON válido.")
        return {}
    except Exception as e:
        print(f"Error inesperado al leer el archivo de configuración: {e}")
        return {}

def get_api_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Obtiene la configuración específica de la API.
    
    :param config: Diccionario de configuración completo
    :return: Diccionario con la configuración de la API
    """
    return config.get('apiKey', {})

def get_api():
    return get_api_config(load_config())
