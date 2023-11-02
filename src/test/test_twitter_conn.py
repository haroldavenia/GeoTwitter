import pytest

from src.services.TwitterConnection import TwitterConnection

# Inicializa la conexión de Twitter una vez para todas las pruebas
twitter_conn = TwitterConnection()


# Prueba de conexión de Twitter
def test_twitter_connection():
    """
    Verifica si la conexión de Twitter está establecida correctamente.
    """
    assert twitter_conn.is_connected(), "Twitter connection is not established"


# Prueba de solicitud de búsqueda en Twitter
def test_request():
    """
    Realiza una solicitud de búsqueda en Twitter y verifica si el DataFrame resultante no está vacío.
    """
    req_str = 'Ohio (derailment OR accident OR trains OR chemicals OR chernobyl OR disaster)'
    df_result = twitter_conn.search_recent(req_str)
    assert not df_result.empty, "Error in Twitter search: DataFrame is empty"
