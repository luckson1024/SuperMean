# Directory: backend/memory/
# File: vector_memory.py
# Description: Vector-based memory implementation with multi-agent support.

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import faiss
import numpy as np

from backend.memory.base_memory import BaseMemory
from backend.utils.logger import setup_logger
from backend.utils.error_handler import MemoryError

# Initialize logger
log = setup_logger(name="vector_memory")

# Default configuration values
DEFAULT_VECTOR_DIM = 1536  # Default for OpenAI embeddings
DEFAULT_INDEX_PATH = "./vector_memory_index"
DEFAULT_NAMESPACE = "global"  # Default namespace for shared memory

class VectorMemory(BaseMemory):
    """
    Vector-based memory implementation with multi-agent support.
    
    Features:
    - Efficient vector storage using FAISS
    - Namespaced memory segments for agent isolation
    - Shared global context accessible by all agents
    - Cross-agent memory permissions
    - Memory synchronization for concurrent access
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 agent_id: Optional[str] = None,
                 embedding_function: Optional[callable] = None):
        """
        Initialize the VectorMemory.
        
        Args:
            config: Optional configuration dictionary
            agent_id: Optional agent identifier for namespaced memory
            embedding_function: Optional function to convert text to embeddings
        """
        super().__init__(config=config)
        
        self.config = config or {}
        self.agent_id = agent_id
        self.embedding_function = embedding_function
        
        # Vector dimension - configurable but has a default
        self.vector_dim = self.config.get("vector_dim", DEFAULT_VECTOR_DIM)
        
        # Index storage path
        self.index_path = self.config.get("index_path", DEFAULT_INDEX_PATH)
        
        # Multi-agent memory settings
        self.default_namespace = self.config.get("default_namespace", DEFAULT_NAMESPACE)
        self.current_namespace = self.agent_id or self.default_namespace
        
        # Namespace permissions - which agents can access which namespaces
        # Format: {namespace: set(agent_ids)}
        self.namespace_permissions: Dict[str, Set[str]] = self.config.get("namespace_permissions", {})
        
        # Initialize namespace for global context that all agents can access
        if DEFAULT_NAMESPACE not in self.namespace_permissions:
            self.namespace_permissions[DEFAULT_NAMESPACE] = set()
        
        # Initialize namespace for this agent if provided
        if self.agent_id and self.agent_id not in self.namespace_permissions:
            self.namespace_permissions[self.agent_id] = {self.agent_id}
        
        # In-memory storage for vector indices and metadata
        # Format: {namespace: {"index": faiss_index, "metadata": {id: metadata}}}
        self._indices: Dict[str, Dict[str, Any]] = {}
        
        # Key-to-ID mapping for each namespace
        # Format: {namespace: {key: id}}
        self._key_to_id: Dict[str, Dict[str, int]] = {}
        
        # ID counter for each namespace
        # Format: {namespace: next_id}
        self._id_counters: Dict[str, int] = {}
        
        # Locks for thread safety
        self._namespace_locks: Dict[str, asyncio.Lock] = {}
        
        # Initialize indices
        self._initialize_indices()
        
        log.info(f"VectorMemory initialized with agent_id: {self.agent_id}, dimension: {self.vector_dim}")
    
    def _initialize_indices(self) -> None:
        """
        Initialize FAISS indices for each namespace.
        """
        # Create index directory if it doesn't exist
        if not os.path.exists(self.index_path):
            os.makedirs(self.index_path, exist_ok=True)
        
        # Initialize global namespace index
        self._ensure_namespace_index(DEFAULT_NAMESPACE)
        
        # Initialize agent-specific namespace index if agent_id is provided
        if self.agent_id:
            self._ensure_namespace_index(self.agent_id)
    
    def _ensure_namespace_index(self, namespace: str) -> None:
        """
        Ensure that a namespace has an initialized index and lock.
        
        Args:
            namespace: The namespace to initialize
        """
        if namespace not in self._indices:
            # Create a new FAISS index for this namespace
            index = faiss.IndexFlatL2(self.vector_dim)
            
            self._indices[namespace] = {
                "index": index,
                "metadata": {}
            }
            self._key_to_id[namespace] = {}
            self._id_counters[namespace] = 0
            self._namespace_locks[namespace] = asyncio.Lock()
            
            # Try to load existing index if available
            index_file = os.path.join(self.index_path, f"{namespace}_index.faiss")
            metadata_file = os.path.join(self.index_path, f"{namespace}_metadata.json")
            
            if os.path.exists(index_file) and os.path.exists(metadata_file):
                try:
                    # Load the index
                    loaded_index = faiss.read_index(index_file)
                    
                    # Load metadata and key mappings
                    with open(metadata_file, 'r') as f:
                        data = json.load(f)
                        metadata = data.get("metadata", {})
                        key_to_id = data.get("key_to_id", {})
                        id_counter = data.get("id_counter", 0)
                    
                    self._indices[namespace]["index"] = loaded_index
                    self._indices[namespace]["metadata"] = metadata
                    self._key_to_id[namespace] = key_to_id
                    self._id_counters[namespace] = id_counter
                    
                    log.info(f"Loaded existing index for namespace '{namespace}' with {loaded_index.ntotal} vectors")
                except Exception as e:
                    log.error(f"Failed to load existing index for namespace '{namespace}': {e}")
    
    async def _save_namespace_index(self, namespace: str) -> None:
        """
        Save the index and metadata for a namespace to disk.
        
        Args:
            namespace: The namespace to save
        """
        if namespace not in self._indices:
            return
        
        try:
            # Save the index
            index_file = os.path.join(self.index_path, f"{namespace}_index.faiss")
            faiss.write_index(self._indices[namespace]["index"], index_file)
            
            # Save metadata and key mappings
            metadata_file = os.path.join(self.index_path, f"{namespace}_metadata.json")
            data = {
                "metadata": self._indices[namespace]["metadata"],
                "key_to_id": self._key_to_id[namespace],
                "id_counter": self._id_counters[namespace]
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(data, f)
            
            log.debug(f"Saved index and metadata for namespace '{namespace}'")
        except Exception as e:
            log.error(f"Failed to save index for namespace '{namespace}': {e}")
    
    def _get_vector_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to a vector embedding.
        
        Args:
            text: The text to convert
            
        Returns:
            A numpy array containing the embedding vector
        """
        if self.embedding_function:
            return self.embedding_function(text)
        else:
            # Placeholder implementation - in a real system, you would use a proper embedding model
            # This is just for testing and should be replaced with actual embeddings
            log.warning("Using placeholder embedding function. Replace with actual embeddings in production.")
            # Create a random vector of the correct dimension
            vector = np.random.rand(self.vector_dim).astype(np.float32)
            # Normalize to unit length
            vector = vector / np.linalg.norm(vector)
            return vector
    
    def _check_namespace_access(self, namespace: str) -> bool:
        """
        Check if the current agent has access to the specified namespace.
        
        Args:
            namespace: The namespace to check access for
            
        Returns:
            True if access is allowed, False otherwise
        """
        # Global namespace is accessible to all
        if namespace == DEFAULT_NAMESPACE:
            return True
        
        # No agent_id means system-level access (allowed)
        if not self.agent_id:
            return True
        
        # Check if the agent is in the allowed set for this namespace
        allowed_agents = self.namespace_permissions.get(namespace, set())
        return len(allowed_agents) == 0 or self.agent_id in allowed_agents
    
    async def _get_namespace_lock(self, namespace: str) -> asyncio.Lock:
        """
        Get the lock for a namespace, creating it if it doesn't exist.
        
        Args:
            namespace: The namespace to get the lock for
            
        Returns:
            An asyncio Lock object
        """
        if namespace not in self._namespace_locks:
            self._namespace_locks[namespace] = asyncio.Lock()
        return self._namespace_locks[namespace]
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None, 
                   namespace: Optional[str] = None) -> bool:
        """
        Store a value with its vector embedding.
        
        Args:
            key: The unique identifier for the memory entry
            value: The data to be stored
            metadata: Optional metadata about the entry
            namespace: Optional namespace to store in (defaults to current namespace)
            
        Returns:
            True if storage was successful, False otherwise
        """
        # Use specified namespace or default to current namespace
        ns = namespace or self.current_namespace
        
        # Check access permissions
        if not self._check_namespace_access(ns):
            log.warning(f"Agent '{self.agent_id}' does not have access to namespace '{ns}'")
            return False
        
        # Ensure namespace index exists
        self._ensure_namespace_index(ns)
        
        # Prepare metadata
        entry_metadata = metadata or {}
        entry_metadata["timestamp"] = datetime.now().isoformat()
        entry_metadata["key"] = key
        
        # If agent_id is available, add it to metadata
        if self.agent_id:
            entry_metadata["agent_id"] = self.agent_id
        
        try:
            # Get text representation for embedding
            if isinstance(value, str):
                text_for_embedding = value
            else:
                # For non-string values, use string representation
                text_for_embedding = str(value)
                # Store original value in metadata
                try:
                    entry_metadata["_original_value"] = json.dumps(value)
                except (TypeError, OverflowError):
                    entry_metadata["_original_value_type"] = str(type(value))
            
            # Get vector embedding
            vector = self._get_vector_embedding(text_for_embedding)
            
            # Acquire lock for this namespace
            async with await self._get_namespace_lock(ns):
                # Check if key already exists
                if key in self._key_to_id[ns]:
                    # Update existing entry
                    entry_id = self._key_to_id[ns][key]
                    # We can't update vectors in FAISS directly, so we need to remove and re-add
                    # This is a limitation of FAISS - in a production system, you might use a different approach
                    log.debug(f"Updating existing entry for key '{key}' in namespace '{ns}'")
                else:
                    # Add new entry
                    entry_id = self._id_counters[ns]
                    self._id_counters[ns] += 1
                    self._key_to_id[ns][key] = entry_id
                    log.debug(f"Adding new entry for key '{key}' in namespace '{ns}'")
                
                # Store vector in the index
                vector_np = np.array([vector], dtype=np.float32)
                self._indices[ns]["index"].add(vector_np)
                
                # Store metadata
                self._indices[ns]["metadata"][entry_id] = entry_metadata
                
                # Save to disk
                asyncio.create_task(self._save_namespace_index(ns))
                
                return True
        except Exception as e:
            log.error(f"Error storing key '{key}' in namespace '{ns}': {e}")
            return False
    
    async def retrieve(self, key: str, namespace: Optional[str] = None) -> Optional[Any]:
        """
        Retrieve a value by key.
        
        Args:
            key: The unique identifier for the memory entry
            namespace: Optional namespace to retrieve from (defaults to current namespace)
            
        Returns:
            The stored value if found, otherwise None
        """
        # Use specified namespace or default to current namespace
        ns = namespace or self.current_namespace
        
        # Check access permissions
        if not self._check_namespace_access(ns):
            log.warning(f"Agent '{self.agent_id}' does not have access to namespace '{ns}'")
            return None
        
        # Check if namespace exists
        if ns not in self._indices:
            log.debug(f"Namespace '{ns}' does not exist")
            return None
        
        # Check if key exists in this namespace
        if key not in self._key_to_id[ns]:
            log.debug(f"Key '{key}' not found in namespace '{ns}'")
            return None
        
        try:
            # Acquire lock for this namespace
            async with await self._get_namespace_lock(ns):
                # Get entry ID
                entry_id = self._key_to_id[ns][key]
                
                # Get metadata
                metadata = self._indices[ns]["metadata"].get(entry_id, {})
                
                # Check if original value was stored in metadata
                if "_original_value" in metadata:
                    try:
                        return json.loads(metadata["_original_value"])
                    except json.JSONDecodeError:
                        log.warning(f"Failed to decode original value for key '{key}'")
                
                # If no original value or decoding failed, return the metadata
                # This is a simplified approach - in a real system, you might handle this differently
                return metadata
        except Exception as e:
            log.error(f"Error retrieving key '{key}' from namespace '{ns}': {e}")
            return None
    
    async def search(self, query: str, top_k: int = 5, 
                    filter_metadata: Optional[Dict[str, Any]] = None,
                    namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for entries similar to the query.
        
        Args:
            query: The search query
            top_k: Maximum number of results to return
            filter_metadata: Optional metadata filters
            namespace: Optional namespace to search in (defaults to current namespace)
            
        Returns:
            List of matching entries with their metadata and similarity scores
        """
        # Use specified namespace or default to current namespace
        ns = namespace or self.current_namespace
        
        # Check access permissions
        if not self._check_namespace_access(ns):
            log.warning(f"Agent '{self.agent_id}' does not have access to namespace '{ns}'")
            return []
        
        # Check if namespace exists
        if ns not in self._indices or self._indices[ns]["index"].ntotal == 0:
            log.debug(f"Namespace '{ns}' does not exist or is empty")
            return []
        
        try:
            # Get vector embedding for the query
            query_vector = self._get_vector_embedding(query)
            query_vector_np = np.array([query_vector], dtype=np.float32)
            
            # Acquire lock for this namespace
            async with await self._get_namespace_lock(ns):
                # Get the number of vectors in the index
                num_vectors = self._indices[ns]["index"].ntotal
                
                # Adjust top_k if necessary
                actual_top_k = min(top_k, num_vectors)
                
                # Perform the search
                distances, indices = self._indices[ns]["index"].search(query_vector_np, actual_top_k)
                
                # Process results
                results = []
                for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                    # Skip invalid indices (FAISS might return -1 for not enough results)
                    if idx < 0:
                        continue
                    
                    # Get metadata for this entry
                    metadata = self._indices[ns]["metadata"].get(idx, {})
                    
                    # Apply metadata filters if provided
                    if filter_metadata and not self._matches_filter(metadata, filter_metadata):
                        continue
                    
                    # Calculate similarity score (convert distance to similarity)
                    similarity = 1.0 / (1.0 + distance)
                    
                    # Add to results
                    results.append({
                        "key": metadata.get("key", f"unknown_{idx}"),
                        "metadata": metadata,
                        "similarity": similarity,
                        "distance": float(distance)
                    })
                
                return results
        except Exception as e:
            log.error(f"Error searching in namespace '{ns}': {e}")
            return []
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_metadata: Dict[str, Any]) -> bool:
        """
        Check if metadata matches the filter criteria.
        
        Args:
            metadata: The metadata to check
            filter_metadata: The filter criteria
            
        Returns:
            True if metadata matches all filter criteria, False otherwise
        """
        for key, value in filter_metadata.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True
    
    async def delete(self, key: str, namespace: Optional[str] = None) -> bool:
        """
        Delete an entry by key.
        
        Args:
            key: The unique identifier for the memory entry
            namespace: Optional namespace to delete from (defaults to current namespace)
            
        Returns:
            True if deletion was successful, False otherwise
        """
        # Use specified namespace or default to current namespace
        ns = namespace or self.current_namespace
        
        # Check access permissions
        if not self._check_namespace_access(ns):
            log.warning(f"Agent '{self.agent_id}' does not have access to namespace '{ns}'")
            return False
        
        # Check if namespace exists
        if ns not in self._indices:
            log.debug(f"Namespace '{ns}' does not exist")
            return True  # Consider it a success if namespace doesn't exist
        
        # Check if key exists in this namespace
        if key not in self._key_to_id[ns]:
            log.debug(f"Key '{key}' not found in namespace '{ns}'")
            return True  # Consider it a success if key doesn't exist
        
        try:
            # Acquire lock for this namespace
            async with await self._get_namespace_lock(ns):
                # Get entry ID
                entry_id = self._key_to_id[ns][key]
                
                # Remove from key mapping
                del self._key_to_id[ns][key]
                
                # Remove from metadata
                if entry_id in self._indices[ns]["metadata"]:
                    del self._indices[ns]["metadata"][entry_id]
                
                # Note: We can't easily remove vectors from FAISS indices
                # In a production system, you might mark entries as deleted and rebuild the index periodically
                # or use a different vector store that supports deletion
                
                # Save changes to disk
                asyncio.create_task(self._save_namespace_index(ns))
                
                log.debug(f"Deleted key '{key}' from namespace '{ns}'")
                return True
        except Exception as e:
            log.error(f"Error deleting key '{key}' from namespace '{ns}': {e}")
            return False
    
    async def grant_namespace_access(self, namespace: str, agent_id: str) -> bool:
        """
        Grant an agent access to a namespace.
        
        Args:
            namespace: The namespace to grant access to
            agent_id: The agent to grant access to
            
        Returns:
            True if access was granted, False otherwise
        """
        # Only allow if current agent has access to the namespace
        if not self._check_namespace_access(namespace):
            log.warning(f"Agent '{self.agent_id}' cannot grant access to namespace '{namespace}'")
            return False
        
        # Update permissions
        if namespace not in self.namespace_permissions:
            self.namespace_permissions[namespace] = set()
        
        self.namespace_permissions[namespace].add(agent_id)
        log.info(f"Granted agent '{agent_id}' access to namespace '{namespace}'")
        return True
    
    async def revoke_namespace_access(self, namespace: str, agent_id: str) -> bool:
        """
        Revoke an agent's access to a namespace.
        
        Args:
            namespace: The namespace to revoke access from
            agent_id: The agent to revoke access from
            
        Returns:
            True if access was revoked, False otherwise
        """
        # Only allow if current agent has access to the namespace
        if not self._check_namespace_access(namespace):
            log.warning(f"Agent '{self.agent_id}' cannot revoke access to namespace '{namespace}'")
            return False
        
        # Cannot revoke access to global namespace
        if namespace == DEFAULT_NAMESPACE:
            log.warning("Cannot revoke access to global namespace")
            return False
        
        # Update permissions
        if namespace in self.namespace_permissions and agent_id in self.namespace_permissions[namespace]:
            self.namespace_permissions[namespace].remove(agent_id)
            log.info(f"Revoked agent '{agent_id}' access to namespace '{namespace}'")
            return True
        
        return False
    
    async def list_namespaces(self) -> List[str]:
        """
        List all available namespaces that the current agent has access to.
        
        Returns:
            List of namespace names
        """
        if not self.agent_id:
            # System-level access - return all namespaces
            return list(self._indices.keys())
        
        # Filter namespaces by access permissions
        accessible_namespaces = [ns for ns in self._indices.keys() if self._check_namespace_access(ns)]
        return accessible_namespaces
    
    async def switch_namespace(self, namespace: str) -> bool:
        """
        Switch the current namespace for this memory instance.
        
        Args:
            namespace: The namespace to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        # Check access permissions
        if not self._check_namespace_access(namespace):
            log.warning(f"Agent '{self.agent_id}' does not have access to namespace '{namespace}'")
            return False
        
        # Ensure namespace exists
        self._ensure_namespace_index(namespace)
        
        # Switch namespace
        self.current_namespace = namespace
        log.debug(f"Switched to namespace '{namespace}'")
        return True
    
    async def create_shared_context(self, context_id: str, initial_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new shared context namespace that multiple agents can access.
        
        Args:
            context_id: Identifier for the shared context
            initial_data: Optional initial data to store in the context
            
        Returns:
            The namespace name for the shared context
        """
        # Create namespace name for the shared context
        namespace = f"shared_{context_id}"
        
        # Ensure namespace exists
        self._ensure_namespace_index(namespace)
        
        # Initialize permissions - empty set means all agents can access
        self.namespace_permissions[namespace] = set()
        
        # Store initial data if provided
        if initial_data:
            for key, value in initial_data.items():
                await self.store(key, value, namespace=namespace)
        
        log.info(f"Created shared context '{context_id}' with namespace '{namespace}'")
        return namespace
    
    async def join_shared_context(self, context_id: str) -> bool:
        """
        Join an existing shared context.
        
        Args:
            context_id: Identifier for the shared context
            
        Returns:
            True if join was successful, False otherwise
        """
        namespace = f"shared_{context_id}"
        
        # Check if namespace exists
        if namespace not in self._indices:
            log.warning(f"Shared context '{context_id}' does not exist")
            return False
        
        # Switch to this namespace
        return await self.switch_namespace(namespace)
    
    async def sync_with_global(self, keys: List[str]) -> int:
        """
        Synchronize specified keys from global namespace to current namespace.
        
        Args:
            keys: List of keys to synchronize
            
        Returns:
            Number of keys successfully synchronized
        """
        if self.current_namespace == DEFAULT_NAMESPACE:
            log.warning("Already in global namespace, no need to sync")
            return 0
        
        synced_count = 0
        for key in keys:
            # Retrieve from global namespace
            value = await self.retrieve(key, namespace=DEFAULT_NAMESPACE)
            if value is not None:
                # Store in current namespace
                success = await self.store(key, value)
                if success:
                    synced_count += 1
        
        log.info(f"Synchronized {synced_count} keys from global namespace to '{self.current_namespace}'")
        return synced_count