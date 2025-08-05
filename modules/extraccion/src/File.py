import collections
import os
import glob
import time
import yaml
import pandas as pd
import polars as pl
import sqlite3
import gc
import psutil
import sys

MODULE_BASE = os.path.dirname(os.path.dirname(__file__))

class File:
    """Clase base genérica para representar un fichero."""
    def __init__(self, name, path):
        self.name = name
        self.path = path

class SQLiteFileLoader:
    def __init__(self):
        self._db_path = None

    def load(self, extractor_file):
        self._ensure_db_polars(extractor_file)
        conn = sqlite3.connect(self._db_path)
        df = pd.read_sql_query("SELECT * FROM data", conn)
        conn.close()
        df = df.astype(str)
        df.columns = [str(x).upper().strip() for x in df.columns]
        return df

    def load_partial(self, extractor_file, columns):
        self._ensure_db_polars(extractor_file)
        conn = sqlite3.connect(self._db_path)
        cols = ','.join([f'"{col}"' for col in columns])
        query = f"SELECT {cols} FROM data"
        df = pd.read_sql_query(query, conn)
        conn.close()
        df = df.astype(str)
        df.columns = [str(x).upper().strip() for x in df.columns]
        return df

    def _ensure_db_polars(self, extractor_file):
        if self._db_path is None:
            db_dir = os.path.join(extractor_file.file_path, ".sqlite_cache")
            os.makedirs(db_dir, exist_ok=True)
            db_name = f"{extractor_file.file}_cache.sqlite"
            self._db_path = os.path.join(db_dir, db_name)
        if not os.path.exists(self._db_path):
            print("cargando la base de datos con polars")
            metadata = extractor_file.config_content['metadata']
            file_path = extractor_file.find_file(extractor_file.file_path, extractor_file.file, metadata["Extension"])
            estructura = extractor_file.config_content['structure']
            try:
                column_names = [campo["name"].upper() for campo in estructura]
                if not metadata.get("Header", True):
                    pl_df = pl.read_csv(
                        file_path,
                        separator=metadata["Separator"],
                        encoding=metadata["Encoding"],
                        has_header=False,
                        new_columns=column_names
                    )
                else:
                    pl_df = pl.read_csv(
                        file_path,
                        separator=metadata["Separator"],
                        encoding=metadata["Encoding"],
                        has_header=True
                    )
                pl_df = pl_df.with_columns([pl.col(col).cast(pl.Utf8) for col in pl_df.columns])
                pl_df = pl_df.with_row_count("LINE_NUMBER", offset=1)
                df = pl_df.to_pandas()
                df = df.astype(str)
                df.columns = [str(x).upper().strip() for x in df.columns]
                del pl_df
                gc.collect()
            except Exception:
                print("cargando la base de datos con pandas")
                if not metadata.get("Header", True):
                    column_names = [campo["name"].upper() for campo in estructura]
                    df = pd.read_csv(
                        file_path,
                        sep=metadata["Separator"],
                        encoding=metadata["Encoding"],
                        dtype=str,
                        keep_default_na=False,
                        header=None,
                        names=column_names
                    )
                    df.columns = [str(x).upper().strip() for x in column_names]
                else:
                    df = pd.read_csv(
                        file_path,
                        sep=metadata["Separator"],
                        encoding=metadata["Encoding"],
                        dtype=str,
                        keep_default_na=False,
                        header=0
                    )
                    df.columns = [str(x).upper().strip() for x in df.columns]
                df.insert(0, "LINE_NUMBER", range(1, len(df) + 1))
                df = df.astype(str)
            conn = sqlite3.connect(self._db_path)
            df.to_sql("data", conn, index=False, dtype={col: "TEXT" for col in df.columns})
            conn.close()
            del df
            gc.collect()
        else:
            print("la base de datos ya estaba cargada")

    @staticmethod
    def clear_sqlite_cache(input_folder):
        cache_dir = os.path.join(input_folder, ".sqlite_cache")
        existe = os.path.exists(cache_dir)
        if os.path.exists(cache_dir):
            for fname in os.listdir(cache_dir):
                if fname.endswith("_cache.sqlite"):
                    try:
                        os.remove(os.path.join(cache_dir, fname))
                    except Exception as e:
                        print(f"Error eliminando {fname}: {e}")

class FileContentCache:
    """Caché LRU basada en memoria usada por los ficheros."""
    _cache = collections.OrderedDict()
    _max_bytes = 200 * 1024 * 1024  # 200 MB por defecto, ajusta según tu entorno

    @classmethod
    def get(cls, key):
        if key in cls._cache:
            cls._cache.move_to_end(key)
            return cls._cache[key][0]
        return None

    @classmethod
    def set(cls, key, value):
        size = cls._estimate_size(value)
        cls._cache[key] = (value, size)
        cls._cache.move_to_end(key)
        cls._evict_if_needed()

    @classmethod
    def remove(cls, key):
        if key in cls._cache:
            del cls._cache[key]

    @classmethod
    def clear(cls):
        cls._cache.clear()

    @classmethod
    def _evict_if_needed(cls):
        while cls._total_bytes() > cls._max_bytes and len(cls._cache) > 1:
            cls._cache.popitem(last=False)

    @classmethod
    def _total_bytes(cls):
        return sum(size for _, size in cls._cache.values())

    @staticmethod
    def _estimate_size(obj):
        # Estima el tamaño en bytes del objeto (DataFrame)
        try:
            if hasattr(obj, 'memory_usage'):
                # pandas DataFrame
                return int(obj.memory_usage(deep=True).sum())
            elif hasattr(obj, 'estimated_size'):
                # polars DataFrame
                return int(obj.estimated_size())
            else:
                return sys.getsizeof(obj)
        except Exception:
            return sys.getsizeof(obj)

class ExtractorFile(File):
    """Entidad de fichero de extracción, con soporte para estrategias de carga."""
    def __init__(self, scope, version, file, file_path):
        super().__init__(file, file_path)
        self.scope = scope
        self.version = version
        self.initial_path = os.path.join(MODULE_BASE, 'data/scopes', self.scope)
        self.specific_path = os.path.join(MODULE_BASE, 'data/scopes', self.scope, self.version, self.name)
        self.config_content = self.load_config()
        self._file_content = None  # Lazy loading
        self.log = ''
        self.loader = SQLiteFileLoader()

    @property
    def file_path(self):
        return self.path

    @property
    def file(self):
        return self.name

    @property
    def file_content(self):
        # No cache, siempre carga desde SQLite
        return self.load_file()

    def unload_file_content(self):
        # No hay caché, no hace nada
        pass

    def load_config(self):
        contenido_ficheros = {}
        metadata_path = os.path.join(self.initial_path, 'metadata.yaml')
        with open(metadata_path, 'r', encoding='utf-8') as f:
            contenido_ficheros['metadata'] = yaml.safe_load(f)
        structure_path = os.path.join(self.specific_path, 'structure.yaml')
        with open(structure_path, 'r', encoding='utf-8') as f:
            contenido_ficheros['structure'] = yaml.safe_load(f)
        return contenido_ficheros

    def load_file(self):
        print(f"Cargando contenido de {self.scope}|{self.version}|{self.file_path}|{self.file}...")
        start_load = time.time()
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        file_content = self.loader.load(self)
        mem_after = process.memory_info().rss
        end_load = time.time()
        mem_mb = (mem_after - mem_before) / (1024 * 1024)
        self.log += (f"🕒 Tiempo Carga: {end_load - start_load:.2f} segundos\n")
        self.log += (f"🧠 Memoria consumida: {mem_mb:.2f} MB\n")
        return file_content

    def find_file(self, directorio, nombre_base, extension):
        patron = os.path.join(directorio, f"{nombre_base}*{'.' + extension}")
        archivos = glob.glob(patron)
        if not archivos:
            raise FileNotFoundError(
                f"No se encontró ningún fichero que empiece por '{nombre_base}' y termine en '.{extension}'")
        if len(archivos) > 1:
            print("⚠️ Se encontraron varios ficheros, se usará el primero:")
            for f in archivos:
                print(" -", os.path.basename(f))
        return archivos[0]

    def get_partial_content(self, columns):
        """
        Carga solo las columnas indicadas del fichero, útil para ficheros grandes.
        columns: lista de nombres de columna (en mayúsculas).
        """
        return self.loader.load_partial(self, columns)