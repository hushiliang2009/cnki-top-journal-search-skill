import json

from cnki_search.cli import main


def test_cli_status_is_json_and_does_not_open_browser(capsys) -> None:
    assert main(["status"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "login_required"


def test_cli_help_lists_safe_commands(capsys) -> None:
    assert main(["--help"]) == 0
    output = capsys.readouterr().out
    assert "login" in output
    assert "search" in output
    assert "download" not in output
