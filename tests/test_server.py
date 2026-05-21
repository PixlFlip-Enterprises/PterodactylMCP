import asyncio

from pterodactyl_mcp.server import mcp


def test_server_registers_expected_tools():
    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}

    assert "ptero_ai_search_users" in names
    assert "ptero_ai_search_servers" in names
    assert "ptero_ai_panel_totals" in names

    assert "ptero_app_get_users" in names
    assert "ptero_app_get_servers_server" in names
    assert "ptero_app_delete_nodes_node_allocations_allocation" in names

    assert "ptero_app_list_endpoints" in names
    assert "ptero_app_request" in names


def test_server_registers_prompts():
    prompts = asyncio.run(mcp.list_prompts())
    names = {p.name for p in prompts}
    assert "troubleshoot_server" in names
    assert "provision_user_and_server" in names


def test_server_registers_resources():
    resources = asyncio.run(mcp.list_resources())
    templates = asyncio.run(mcp.list_resource_templates())
    static_uris = {str(r.uri) for r in resources}
    template_uris = {str(t.uri_template) for t in templates}
    all_uris = static_uris | template_uris
    assert any("pterodactyl://panel/overview" in u for u in all_uris)
    assert any("pterodactyl://servers/" in u and "summary" in u for u in all_uris)
