
"""
Унифицированный менеджер кэша для всех API
"""

import os
import glob
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class CacheManager:
    """Унифицированный менеджер кэша"""
    
    def __init__(self, base_cache_dir: str = "data/cache"):
        self.base_cache_dir = Path(base_cache_dir)
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self) -> None:
        """Создание базовой директории кэша"""
        self.base_cache_dir.mkdir(parents=True, exist_ok=True)
    
    def clear_cache_for_source(self, source: str) -> None:
        """
        Очистка кэша для конкретного источника
        
        Args:
            source: Название источника (hh, sj, etc.)
        """
        cache_dir = self.base_cache_dir / source
        if not cache_dir.exists():
            logger.info(f"Cache directory for {source} doesn't exist")
            return
        
        try:
            pattern = f"{source}_*.json"
            cache_files = list(cache_dir.glob(pattern))
            
            for file_path in cache_files:
                file_path.unlink()
                logger.debug(f"Removed cache file: {file_path}")
            
            logger.info(f"Cleared {len(cache_files)} cache files for {source}")
            
        except Exception as e:
            logger.error(f"Error clearing cache for {source}: {e}")
    
    def clear_all_cache(self) -> None:
        """Очистка всего кэша"""
        try:
            cache_files = list(self.base_cache_dir.rglob("*.json"))
            
            for file_path in cache_files:
                file_path.unlink()
                logger.debug(f"Removed cache file: {file_path}")
            
            logger.info(f"Cleared {len(cache_files)} total cache files")
            
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
    
    def get_cache_size(self, source: Optional[str] = None) -> int:
        """
        Получение размера кэша в байтах
        
        Args:
            source: Источник для подсчета (если None - весь кэш)
            
        Returns:
            Размер кэша в байтах
        """
        try:
            if source:
                cache_dir = self.base_cache_dir / source
                pattern = "*.json"
            else:
                cache_dir = self.base_cache_dir
                pattern = "**/*.json"
            
            total_size = 0
            for file_path in cache_dir.glob(pattern):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
            
        except Exception as e:
            logger.error(f"Error calculating cache size: {e}")
            return 0
    
    def get_cache_files_count(self, source: Optional[str] = None) -> int:
        """
        Получение количества файлов в кэше
        
        Args:
            source: Источник для подсчета (если None - весь кэш)
            
        Returns:
            Количество файлов в кэше
        """
        try:
            if source:
                cache_dir = self.base_cache_dir / source
                pattern = "*.json"
            else:
                cache_dir = self.base_cache_dir
                pattern = "**/*.json"
            
            return len(list(cache_dir.glob(pattern)))
            
        except Exception as e:
            logger.error(f"Error counting cache files: {e}")
            return 0


# Глобальный экземпляр менеджера кэша
cache_manager = CacheManager()
