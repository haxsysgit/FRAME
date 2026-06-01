import example_projects.autopahe.ap_core.browser
import example_projects.autopahe.ap_core.platform_paths
import example_projects.autopahe.auto_pahe as auto_pahe


def test_setup_preserves_existing_config(monkeypatch, tmp_path):
    config_path = tmp_path / "config.ini"
    config_path.write_text("[defaults]\nbrowser = firefox\n", encoding="utf-8")

    monkeypatch.setattr(example_projects.autopahe.ap_core.platform_paths, "get_config_dir", lambda: tmp_path)
    monkeypatch.setattr(example_projects.autopahe.ap_core.browser, "install_playwright_browser", lambda browser: True)

    assert auto_pahe.setup_environment()
    assert config_path.read_text(encoding="utf-8") == "[defaults]\nbrowser = firefox\n"
