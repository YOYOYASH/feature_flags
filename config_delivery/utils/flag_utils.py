import json
import hashlib



def normalize_structure(data):
    """
    Ensures nested JSON strings are parsed into real objects 
    and handles recursion for lists/dicts.
    """
    # 1. Handle Strings that might be JSON
    if isinstance(data, str):
        try:
            stripped = data.strip()
            if (stripped.startswith('{') and stripped.endswith('}')) or \
               (stripped.startswith('[') and stripped.endswith(']')):
                return normalize_structure(json.loads(data))
        except (ValueError, TypeError):
            return data

    # 2. Handle Dicts (Recurse)
    if isinstance(data, dict):
        return {k: normalize_structure(v) for k, v in data.items()}

    # 3. Handle Lists (Recurse)
    if isinstance(data, list):
        return [normalize_structure(item) for item in data]

    return data


def get_flag_hash(flags_list):
    """
    Returns (hash_string, normalized_data_object)
    """
    if not flags_list:
        return "empty", []

    # Clean the data
    clean_data = normalize_structure(flags_list)

    # Sort the list of flags by 'flag_key' to ensure list order doesn't matter
    # We use .get() to avoid errors if a key is missing
    sorted_data = sorted(clean_data, key=lambda x: x.get('flag_key', ''))

    # Dump to string with deterministic ordering
    canonical_str = json.dumps(
        sorted_data, 
        sort_keys=True,       # Sorts dictionary keys (enabled, flag_key, etc.)
        separators=(',', ':') # Removes whitespace
    )

    # Generate SHA256 Hash
    return hashlib.sha256(canonical_str.encode()).hexdigest(), sorted_data