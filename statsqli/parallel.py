"""
Parallel extraction module for safe concurrent character extraction.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Callable, Dict
from .extractor import BinarySearchExtractor
import threading


class ParallelExtractor:
    """Extracts multiple characters in parallel when safe."""
    
    def __init__(self, extractor: BinarySearchExtractor, max_workers: int = 4):
        """
        Initialize parallel extractor.
        
        Args:
            extractor: BinarySearchExtractor instance to use
            max_workers: Maximum number of parallel workers
        """
        self.extractor = extractor
        self.max_workers = max_workers
        self.lock = threading.Lock()
    
    def extract_characters_parallel(self, positions: List[int], 
                                   table: str = "users",
                                   column: str = "username",
                                   where_clause: str = "1=1") -> Dict[int, Optional[str]]:
        """
        Extract multiple characters in parallel.
        
        Args:
            positions: List of character positions to extract
            table: Table name to query
            column: Column name to extract from
            where_clause: WHERE clause for the query
            
        Returns:
            Dictionary mapping position to extracted character
        """
        results: Dict[int, Optional[str]] = {}
        
        def extract_one(position: int) -> tuple:
            """Extract a single character."""
            char = self.extractor.extract_character_binary(
                position, table, column, where_clause
            )
            return position, char
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all extraction tasks
            futures = {
                executor.submit(extract_one, pos): pos 
                for pos in positions
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                position, char = future.result()
                results[position] = char
                
                with self.lock:
                    extracted = [v for v in results.values() if v is not None]
                    print(f"[*] Parallel extraction progress: {len(extracted)}/{len(positions)}", 
                          end='\r')
        
        print()  # New line after progress
        return results
    
    def extract_string_chunks(self, table: str = "users", 
                             column: str = "username",
                             where_clause: str = "1=1",
                             chunk_size: int = 4,
                             max_length: int = 100) -> str:
        """
        Extract string in chunks using parallel extraction.
        
        Args:
            table: Table name to query
            column: Column name to extract from
            where_clause: WHERE clause for the query
            chunk_size: Number of characters to extract in parallel
            max_length: Maximum string length to extract
            
        Returns:
            Extracted string
        """
        result_chars: Dict[int, str] = {}
        
        # Extract in chunks
        for start_pos in range(1, max_length + 1, chunk_size):
            end_pos = min(start_pos + chunk_size - 1, max_length)
            positions = list(range(start_pos, end_pos + 1))
            
            chunk_results = self.extract_characters_parallel(
                positions, table, column, where_clause
            )
            
            result_chars.update(chunk_results)
            
            # Check if we should stop (found null or end)
            if None in chunk_results.values():
                break
        
        # Reconstruct string in order
        result = ""
        for pos in sorted(result_chars.keys()):
            char = result_chars[pos]
            if char is None:
                break
            result += char
            if char in ['\x00', '\n', '\r']:
                break
        
        return result.rstrip('\x00\n\r')

