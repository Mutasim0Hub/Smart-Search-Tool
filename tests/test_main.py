from smart_search import main as main_module


def test_main_prints_banner_before_main_menu(monkeypatch, capsys) -> None:
    events = []
    monkeypatch.setattr(main_module, "show_main_menu", lambda: events.append("menu"))
    monkeypatch.setattr("builtins.input", lambda _prompt="": "0")

    main_module.main()

    output = capsys.readouterr().out
    assert output.startswith(main_module.BANNER + "\n")
    assert events == ["menu"]
