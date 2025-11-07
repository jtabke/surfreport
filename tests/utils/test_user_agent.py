from types import SimpleNamespace

from surf_report.utils import user_agent


class DummyResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("HTTP error")


def test_get_user_agent_fetches_first_entry(monkeypatch, load_text_fixture):
    monkeypatch.delenv(user_agent.ENV_USER_AGENT, raising=False)
    user_agent.clear_cached_user_agent()
    html = load_text_fixture("useragents_me_sample.html")

    monkeypatch.setattr(
        user_agent,
        "requests",
        SimpleNamespace(get=lambda url, timeout: DummyResponse(html)),
    )

    ua = user_agent.get_user_agent()
    assert "Windows NT 10.0" in ua
    assert "\n" not in ua


def test_get_user_agent_respects_env_override(monkeypatch):
    monkeypatch.setenv(user_agent.ENV_USER_AGENT, "MyCrawler/1.0")
    user_agent.clear_cached_user_agent()

    assert user_agent.get_user_agent() == "MyCrawler/1.0"


def test_get_user_agent_falls_back_to_default(monkeypatch):
    monkeypatch.delenv(user_agent.ENV_USER_AGENT, raising=False)
    user_agent.clear_cached_user_agent()

    class FakeRequestException(Exception):
        pass

    def failing_get(*_, **__):
        raise FakeRequestException("network down")

    monkeypatch.setattr(
        user_agent,
        "requests",
        SimpleNamespace(get=failing_get, RequestException=FakeRequestException),
    )

    assert user_agent.get_user_agent() == user_agent.DEFAULT_USER_AGENT
