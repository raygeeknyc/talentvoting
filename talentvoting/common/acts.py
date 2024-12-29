from typing import List, Dict

# For now an Act is a JSON object with no stricter definition
Act = Dict[str, any]

# Any number of Acts are often referenced as a group
Acts = List[Act]