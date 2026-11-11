"""
Skill Embeddings Cache - Manage skill embeddings for semantic matching
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np
from functools import lru_cache

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"
EMBEDDINGS_PATH = MODELS_DIR / "skill_embeddings.npy"
SKILL_NAMES_PATH = MODELS_DIR / "skill_names.json"


class EmbeddingsCache:
    """Manages skill embeddings with lazy loading and persistence."""

    def __init__(
        self,
        embeddings_path: Path = EMBEDDINGS_PATH,
        skill_names_path: Path = SKILL_NAMES_PATH
    ):
        self.embeddings_path = embeddings_path
        self.skill_names_path = skill_names_path
        self._embeddings: Optional[np.ndarray] = None
        self._skill_names: Optional[List[str]] = None
        self._skill_to_index: Optional[Dict[str, int]] = None

    @property
    def embeddings(self) -> np.ndarray:
        """Lazy load embeddings array."""
        if self._embeddings is None:
            self.load()
        return self._embeddings

    @property
    def skill_names(self) -> List[str]:
        """Lazy load skill names list."""
        if self._skill_names is None:
            self.load()
        return self._skill_names

    @property
    def skill_to_index(self) -> Dict[str, int]:
        """Get skill name to index mapping."""
        if self._skill_to_index is None and self._skill_names is not None:
            self._skill_to_index = {name: i for i, name in enumerate(self._skill_names)}
        return self._skill_to_index or {}

    def is_loaded(self) -> bool:
        """Check if embeddings are loaded."""
        return self._embeddings is not None

    def load(self) -> bool:
        """Load embeddings from disk."""
        try:
            if self.embeddings_path.exists() and self.skill_names_path.exists():
                self._embeddings = np.load(self.embeddings_path)
                with open(self.skill_names_path, "r", encoding="utf-8") as f:
                    self._skill_names = json.load(f)

                # Build index mapping
                self._skill_to_index = {name: i for i, name in enumerate(self._skill_names)}

                logger.info(f"Loaded {len(self._skill_names)} skill embeddings from cache")
                return True
            else:
                logger.warning("Embeddings cache not found")
                return False
        except Exception as e:
            logger.error(f"Failed to load embeddings cache: {e}")
            return False

    def save(self, embeddings: np.ndarray, skill_names: List[str]) -> bool:
        """Save embeddings to disk."""
        try:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            np.save(self.embeddings_path, embeddings)
            with open(self.skill_names_path, "w", encoding="utf-8") as f:
                json.dump(skill_names, f, ensure_ascii=False, indent=2)

            self._embeddings = embeddings
            self._skill_names = skill_names
            self._skill_to_index = {name: i for i, name in enumerate(skill_names)}

            logger.info(f"Saved {len(skill_names)} skill embeddings to cache")
            return True
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
            return False

    def get_embedding(self, skill_name: str) -> Optional[np.ndarray]:
        """Get embedding for a single skill."""
        idx = self.skill_to_index.get(skill_name)
        if idx is not None and self._embeddings is not None:
            return self._embeddings[idx]
        return None

    def get_embeddings(self, skill_names: List[str]) -> np.ndarray:
        """Get embeddings for multiple skills."""
        indices = [self.skill_to_index.get(name) for name in skill_names]
        valid_indices = [i for i in indices if i is not None]

        if not valid_indices:
            return np.array([])

        return self._embeddings[valid_indices]

    def clear(self):
        """Clear cached embeddings."""
        self._embeddings = None
        self._skill_names = None
        self._skill_to_index = None


# Global cache instance
_cache_instance: Optional[EmbeddingsCache] = None


def get_embeddings_cache() -> EmbeddingsCache:
    """Get singleton EmbeddingsCache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = EmbeddingsCache()
    return _cache_instance


@lru_cache(maxsize=1)
def get_cached_skill_embeddings() -> tuple:
    """
    Get cached skill embeddings as tuple (embeddings_array, skill_names_list).
    Uses lru_cache for module-level singleton pattern.
    """
    cache = get_embeddings_cache()
    if cache.is_loaded():
        return cache.embeddings, cache.skill_names
    return np.array([]), []


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    cache = get_embeddings_cache()
    if cache.load():
        print(f"Loaded {len(cache.skill_names)} skills")
        print(f"Embeddings shape: {cache.embeddings.shape}")
    else:
        print("No cache found")
        sys.exit(1)