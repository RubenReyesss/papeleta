from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuracion de la aplicacion leida desde variables de entorno.
    Pydantic valida los tipos automaticamente al arrancar.
    """

    # URL del servidor Ollama
    ollama_host: str = "http://localhost:11434"

    # Nombre del modelo tal como lo conoce Ollama
    model_name: str = "gemma4:e4b"

    # Ruta del fichero SQLite para el historial de analisis
    db_path: str = "./history.db"

    # Tamano maximo de fichero que acepta el endpoint de subida
    max_file_mb: int = 20

    # Puerto del servidor (uvicorn lo lee directamente)
    port: int = 8000

    @property
    def ollama_chat_url(self) -> str:
        """URL completa del endpoint de chat de Ollama."""
        return f"{self.ollama_host}/api/chat"

    @property
    def ollama_tags_url(self) -> str:
        """URL para consultar los modelos disponibles en Ollama."""
        return f"{self.ollama_host}/api/tags"

    @property
    def max_file_bytes(self) -> int:
        """Tamano maximo en bytes calculado desde MB."""
        return self.max_file_mb * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
