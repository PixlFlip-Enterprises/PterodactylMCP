from pterodactyl_mcp.routes import APPLICATION_ROUTES
from pterodactyl_mcp.server import _tool_name


def test_routes_have_required_keys():
    for route in APPLICATION_ROUTES:
        assert set(route.keys()) >= {"method", "path"}
        assert route["method"] in {"GET", "POST", "PUT", "PATCH", "DELETE"}
        assert route["path"].startswith("/api/application/")


def test_no_duplicate_tool_names():
    names = [_tool_name(r["method"], r["path"]) for r in APPLICATION_ROUTES]
    assert len(names) == len(set(names)), "Duplicate generated tool names"


def test_tool_name_format():
    assert _tool_name("GET", "/api/application/users") == "ptero_app_get_users"
    assert _tool_name("GET", "/api/application/users/{user}") == "ptero_app_get_users_user"
    assert (
        _tool_name("DELETE", "/api/application/nodes/{node}/allocations/{allocation}")
        == "ptero_app_delete_nodes_node_allocations_allocation"
    )
