from permit import envfile


def test_parses_notepad_style_files():
    text = '﻿# keys\r\nNEBIUS_API_KEY="abc=123"\r\n\r\nexport TAVILY_API_KEY=tvly-x\r\nHF_TOKEN=\'hf_y\'\r\nnot a line\r\n'
    assert envfile.parse(text.lstrip("﻿")) == {"NEBIUS_API_KEY": "abc=123", "TAVILY_API_KEY": "tvly-x",
                                                    "HF_TOKEN": "hf_y"}


def test_the_project_env_comes_first_and_the_environment_wins(tmp_path):
    project, home = tmp_path / ".env", tmp_path / "home.env"
    project.write_text("NEBIUS_API_KEY=from-project\nHF_TOKEN=from-project\n", encoding="utf-8-sig")
    home.write_text("NEBIUS_API_KEY=from-home\nTAVILY_API_KEY=from-home\n")
    env = {"HF_TOKEN": "already-set"}
    assert envfile.load([str(project), str(home)], env) == str(project)
    assert env == {"NEBIUS_API_KEY": "from-project", "HF_TOKEN": "already-set"}  # home isn't read once .env exists


def test_falls_back_to_the_home_file_and_tolerates_none(tmp_path):
    home = tmp_path / "home.env"
    home.write_text("TAVILY_API_KEY=t\n")
    env = {}
    assert envfile.load([str(tmp_path / "missing"), str(home)], env) == str(home) and env == {"TAVILY_API_KEY": "t"}
    assert envfile.load([str(tmp_path / "missing")], {}) is None


def test_the_example_holds_no_secrets_and_env_is_ignored():
    import pathlib
    import subprocess
    root = pathlib.Path(envfile.ROOT)
    example = envfile.parse((root / ".env.example").read_text())
    assert {k for k, v in example.items() if v} <= {"NEBIUS_PROJECT_ID"}
    assert subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=root).returncode == 0
