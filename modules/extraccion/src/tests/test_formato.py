import os
import re
import sqlite3
import psutil
from collections import defaultdict
from PySide6.QtCore import QThread

import pandas as pd

from modules.extraccion.src.tests import TestExtractor
from modules.extraccion.src.tests.test_base import EmptyConfig, EmptyFile


class TestFormato(TestExtractor):
    name = 'Formato'

    def __init__(self, extractor_file):
        super().__init__(extractor_file)
        self._abort = False  # Flag para abortar

    def run(self):
        # Comprueba el flag de abortar en cada campo
        if getattr(self, "_abort", False):
            self.launch_warning("Test abortado por el usuario.")
            return
        try:
            import time
            start_validation = time.time()
            import psutil
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss
            file_size = os.path.getsize(self.extractor_file.find_file(
                self.extractor_file.file_path,
                self.extractor_file.file,
                self.extractor_file.config_content['metadata']['Extension']
            ))
            self.is_big_file = file_size > 100 * 1024 * 1024
            validaciones = self.validar_sqlite()
            mem_after = process.memory_info().rss
            end_validation = time.time()
            mem_mb = (mem_after - mem_before) / (1024 * 1024)
            self.log += (f"🕒 Tiempo Validacion: {end_validation - start_validation:.2f} segundos\n")
            self.log += (f"🧠 Memoria consumida en validación: {mem_mb:.2f} MB\n")
            if len(validaciones) == 0:
                self.launch_ok('Todo OK!')
            else:
                self.launch_error('Han fallado algunas validaciones!')
                self.errors = validaciones
            self.clear()
        except EmptyConfig as e:
            self.launch_error(e)
            self.clear()
        except EmptyFile as e:
            self.launch_warning(e)
            self.clear()
        except Exception as e:
            self.launch_error(e)
            self.clear()

    def abort(self):
        self._abort = True

    def validar_sqlite(self):
        estructura = self.extractor_file.config_content['structure']
        errores_por_campo = defaultdict(lambda: defaultdict(list))
        self.extractor_file.loader._ensure_db_polars(self.extractor_file)
        db_path = self.extractor_file.loader._db_path
        conn = sqlite3.connect(db_path)
        table_name = "data"
        for campo in estructura:
            if getattr(self, "_abort", False):
                print("Abortando validación en campo:", campo['name'])
                break
            nombre = campo['name'].upper()
            print(f'validando campo: {nombre}')
            tipo = campo['type'].upper()
            tamaño = campo.get('size')
            precision = campo.get('precision', 0)
            if tipo == 'VARCHAR' and tamaño:
                query = f"""
                    SELECT LINE_NUMBER, "{nombre}"
                    FROM {table_name}
                    WHERE LENGTH("{nombre}") > {tamaño}
                """
                for row in conn.execute(query):
                    if getattr(self, "_abort", False):
                        print("Abortando validación durante query VARCHAR:", nombre)
                        break
                    errores_por_campo[nombre]["Longitud mayor que tamaño permitido"].append((row[0], row[1]))
            elif tipo == 'INTEGER':
                query = f"""
                    SELECT LINE_NUMBER, "{nombre}"
                    FROM {table_name}
                    WHERE NOT ("{nombre}" GLOB '-[0-9]*' OR "{nombre}" GLOB '[0-9]*')
                """
                for row in conn.execute(query):
                    if getattr(self, "_abort", False):
                        print("Abortando validación durante query INTEGER:", nombre)
                        break
                    errores_por_campo[nombre]["Valor no numérico"].append((row[0], row[1]))
                if tamaño:
                    query = f"""
                        SELECT LINE_NUMBER, "{nombre}"
                        FROM {table_name}
                        WHERE LENGTH(REPLACE("{nombre}", '-', '')) > {tamaño}
                    """
                    for row in conn.execute(query):
                        if getattr(self, "_abort", False):
                            print("Abortando validación durante query INTEGER tamaño:", nombre)
                            break
                        errores_por_campo[nombre]["Longitud mayor que tamaño permitido"].append((row[0], row[1]))
            elif tipo == 'DECIMAL':
                if tamaño is None or precision is None:
                    errores_por_campo[nombre]["Falta tamaño o precisión"].append(("TODAS", None))
                    continue
                enteros = tamaño - precision
                query = f"""
                    SELECT LINE_NUMBER, "{nombre}"
                    FROM {table_name}
                    WHERE NOT ("{nombre}" GLOB '-[0-9]*.[0-9]*' OR "{nombre}" GLOB '[0-9]*.[0-9]*' OR "{nombre}" GLOB '-[0-9]*' OR "{nombre}" GLOB '[0-9]*')
                """
                for row in conn.execute(query):
                    if getattr(self, "_abort", False):
                        print("Abortando validación durante query DECIMAL:", nombre)
                        break
                    errores_por_campo[nombre]["Valor no decimal"].append((row[0], row[1]))
                # Exceso de dígitos enteros
                query = f"""
                    SELECT LINE_NUMBER, "{nombre}"
                    FROM {table_name}
                    WHERE LENGTH(SUBSTR("{nombre}", 1, INSTR("{nombre}", '.')-1)) > {enteros}
                """
                for row in conn.execute(query):
                    if getattr(self, "_abort", False):
                        print("Abortando validación durante query DECIMAL enteros:", nombre)
                        break
                    errores_por_campo[nombre]["Exceso de dígitos enteros"].append((row[0], row[1]))
                # Exceso de decimales
                query = f"""
                    SELECT LINE_NUMBER, "{nombre}"
                    FROM {table_name}
                    WHERE LENGTH(SUBSTR("{nombre}", INSTR("{nombre}", '.')+1)) > {precision}
                """
                for row in conn.execute(query):
                    if getattr(self, "_abort", False):
                        print("Abortando validación durante query DECIMAL decimales:", nombre)
                        break
                    errores_por_campo[nombre]["Exceso de decimales"].append((row[0], row[1]))
            # ...otros tipos...
        conn.close()
        return self.convertir_a_dict(errores_por_campo)