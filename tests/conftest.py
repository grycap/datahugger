from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def _parse_repositories(test_config):
    return (
        test_config["location"],
        test_config.get("files", []),
        test_config.get("ignored_files", []),
        test_config.get("options", {}),
    )


def pytest_addoption(parser):
    parser.addoption("--service", action="store", default=None, help="Service to test")


def pytest_generate_tests(metafunc):
    with open(Path("tests", "test_repositories.toml"), "rb") as f:
        test_repos = tomllib.load(f)

    if "location" in metafunc.fixturenames:
        if service_value := metafunc.config.option.service:
            if service_value not in test_repos:
                raise ValueError(f"Unknown service {service_value}")
            metafunc.parametrize(
                "location,files,ignored_files,dh_kwargs",
                [_parse_repositories(repo) for repo in test_repos[service_value]],
            )
        else:
            metafunc.parametrize(
                "location,files,ignored_files,dh_kwargs",
                [
                    _parse_repositories(repo)
                    for service_repos in test_repos.values()
                    for repo in service_repos
                ],
            )
