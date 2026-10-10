"""Explicit drawing roles, not proof of a part's mechanical function.

Custom connector declarations require source/manual review. Native qualification
also checks exact identity and all contact types; a role alone is not evidence.
"""


def is_connector(component):
    namespace = str(component.get("lib_id", "")).partition(":")[0]
    role = component.get("fields", {}).get("ComponentRole")
    return role == "connector" or (role is None and
           (namespace == "Connector" or namespace.startswith("Connector_")))
