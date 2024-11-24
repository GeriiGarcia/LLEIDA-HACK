import unittest
from unittest.mock import patch, MagicMock
from python_functions import db_connect as db

class TestDBConnect(unittest.TestCase):

    @patch('psycopg2.connect')
    def test_connect_to_db_success(self, mock_connect):
        # Configurar el mock para la conexión exitosa
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        conn, cur = connect_to_db()

        # Verificar que la conexión y el cursor se devuelven correctamente
        self.assertIsNotNone(conn)
        self.assertIsNotNone(cur)
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()

    @patch('psycopg2.connect')
    def test_connect_to_db_failure(self, mock_connect):
        # Configurar el mock para lanzar una excepción
        mock_connect.side_effect = Exception("Connection error")

        conn, cur = connect_to_db()

        # Verificar que la conexión y el cursor son None
        self.assertIsNone(conn)
        self.assertIsNone(cur)
        mock_connect.assert_called_once()

    def test_close_db_connection(self):
        # Crear mocks para la conexión y el cursor
        mock_conn = MagicMock()
        mock_cur = MagicMock()

        close_db_connection(mock_conn, mock_cur)

        # Verificar que se llamaron los métodos close
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_close_db_connection_none(self):
        # Verificar que no se lanzan excepciones si conn y cur son None
        try:
            close_db_connection(None, None)
        except Exception as e:
            self.fail(f"close_db_connection raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()