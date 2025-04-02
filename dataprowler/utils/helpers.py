"""
Utility helper functions for DataProwler.
"""

from typing import Any, Dict, List, Union


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Values from dict2 will override values in dict1 if there's a conflict.
    Nested dictionaries will be merged recursively.
    
    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, merge them recursively
            result[key] = deep_merge(result[key], value)
        else:
            # Otherwise just take the value from dict2
            result[key] = value
            
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """
    Flatten a nested dictionary, joining keys with the separator.
    
    Example:
        {"a": {"b": 1, "c": 2}} becomes {"a.b": 1, "a.c": 2}
    
    Args:
        d: Dictionary to flatten
        parent_key: Prefix for keys
        sep: Separator to use between keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """
    Convert a flattened dictionary back to nested form.
    
    Example:
        {"a.b": 1, "a.c": 2} becomes {"a": {"b": 1, "c": 2}}
    
    Args:
        d: Dictionary with flat keys
        sep: Separator used in keys
        
    Returns:
        Nested dictionary
    """
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result