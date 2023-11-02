import unittest
import json
from src.app import app

class TestAPI(unittest.TestCase):

    def setUp(self):
        # Configura la aplicación para pruebas
        self.app = app.test_client()
        self.app.testing = True

    def test_search_endpoint(self):
        # Prueba la ruta '/search' con un request POST válido
        payload = {
            'client_id': 'head1982',
            'tag_filter': 'Ohio disaster',
            'filter_comm-cmd': 'Ohio (derailment OR accident OR trains OR chemicals OR chernobyl OR disaster)',
            'bbox-filter': {
                'min_lat': 10.0,
                'max_lat': 20.0,
                'min_lon': 30.0,
                'max_lon': 40.0
            }
        }

        response = self.app.post('/search', json=payload)
        data = json.loads(response.data)

        # Asegura que la respuesta sea 201
        self.assertEqual(response.status_code, 201)

        # Verifica la estructura de la respuesta
        self.assertTrue('tenant_id' in data)
        self.assertTrue('query_uuid' in data)
        self.assertTrue('date_saved' in data)

    def test_search_endpoint_no_data(self):
        # Prueba la ruta '/search' con un request POST que no produce datos
        payload = {
            'client_id': 'test_client',
            'tag_filter': 'test_tag',
            'filter_comm-cmd': 'error_command'
        }

        response = self.app.post('/search', json=payload)

        # Asegura que la respuesta sea 204
        self.assertEqual(response.status_code, 204)

    def test_search_endpoint_error(self):
        # Prueba la ruta '/search' con un request POST que genera un error
        payload = {
            'client_id': 'test_client',
            'tag_filter': '',
            'filter_comm-cmd': ''
        }

        response = self.app.post('/search', json=payload)
        data = json.loads(response.data)

        # Asegura que la respuesta sea 500 y contiene un mensaje de error
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
