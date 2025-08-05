import os
import pandas as pd
from collections import defaultdict
from modules.extraccion.src.tests.test_base import TestExtractor, EmptyConfig, EmptyFile, ExtractorFile
from PySide6.QtCore import QThread

class TestPK(TestExtractor):
    name = 'PK'

    def __init__(self, extractor_file):
        super().__init__(extractor_file)
        self._abort = False  # Flag para abortar

    def run(self):
        # Elimina el sleep, solo aborta si se solicita
        if getattr(self, "_abort", False):
            self.launch_warning("Test abortado por el usuario.")
            return
        file_size = os.path.getsize(self.extractor_file.find_file(
            self.extractor_file.file_path,
            self.extractor_file.file,
            self.extractor_file.config_content['metadata']['Extension']
        ))
        validaciones = self.validar_pk_sqlite()
        if len(validaciones) == 0:
            self.launch_ok('Todo OK!')
        else:
            self.launch_error('Han fallado algunas validaciones!')
            self.errors = validaciones
        self.clear()

    def abort(self):
        self._abort = True

    def validar_pk_sqlite(self):
        estructura = self.extractor_file.config_content['structure']
        detalles = defaultdict(lambda: defaultdict(list))
        columnas_pk = [campo['name'].upper() for campo in estructura if campo.get('pk')]

        if not columnas_pk:
            return detalles  # No hay PK definida

        self.extractor_file.loader._ensure_db_polars(self.extractor_file)
        db_path = self.extractor_file.loader._db_path
        import sqlite3
        conn = sqlite3.connect(db_path)
        table_name = "data"
        pk_cols = ','.join([f'"{col}"' for col in columnas_pk])

        # PK sin informar: alguna columna PK vacía o nula
        for col in columnas_pk:
            query = f'''
                SELECT LINE_NUMBER, "{col}"
                FROM {table_name}
                WHERE "{col}" IS NULL OR TRIM("{col}") = ''
            '''
            for row in conn.execute(query):
                detalles[col]["PK sin informar"].append((row[0], row[1]))

        # PK duplicada: filas con mismos valores en todas las columnas PK (incluyendo nulos/vacíos)
        query = f'''
            SELECT {pk_cols}, COUNT(*)
            FROM {table_name}
            GROUP BY {pk_cols}
            HAVING COUNT(*) > 1
        '''
        cursor = conn.execute(query)
        for row in cursor:
            pk_values = {col: row[i] for i, col in enumerate(columnas_pk)}
            count = row[len(columnas_pk)]
            # Busca las líneas que tienen esos valores
            where_pk = ' AND '.join([
                f'("{col}" IS ? OR "{col}" = ?)' if pk_values[col] == '' else f'"{col}" = ?'
                for col in columnas_pk
            ])
            params = []
            for col in columnas_pk:
                val = pk_values[col]
                if val == '':
                    params.extend([None, ''])
                else:
                    params.append(val)
            subquery = f'SELECT LINE_NUMBER FROM {table_name} WHERE {where_pk}'
            for line_row in conn.execute(subquery, params):
                clave = ', '.join(f'{col}={pk_values[col]}' for col in columnas_pk)
                msg = f"PK duplicada: {clave}"
                detalles["__PK__"]["Duplicada"].append((line_row[0], msg))
        conn.close()
        return detalles
