import pytest

from tda.render import jinja_ref
from tda.render.sandbox import JinjaSandbox

MSGS = [{"role": "user", "content": "hi"}]


@pytest.fixture(scope="module")
def sandbox():
    with JinjaSandbox(timeout=3) as s:
        yield s


def test_renders_like_in_process(sandbox):
    t = "{% for m in messages %}<{{ m.role }}>{{ m.content }}{% endfor %}{% if add_generation_prompt %}<a>{% endif %}{{ bos_token }}"
    r = sandbox.render(t, MSGS, special_tokens={"bos_token": "<s>"})
    assert r.ok and r.prompt == jinja_ref.render(t, MSGS, special_tokens={"bos_token": "<s>"}) == "<user>hi<a><s>"


def test_transformers_features(sandbox):
    t = ("{{ tools | tojson }}|{{ strftime_now('%Y') }}|{% generation %}x{% endgeneration %}"
         "|{% for i in range(5) %}{% if i == 2 %}{% break %}{% endif %}{{ i }}{% endfor %}")
    r = sandbox.render(t, MSGS, [{"name": "Zürich"}])
    assert r.prompt == '[{"name": "Zürich"}]|2026|x|01'


@pytest.mark.parametrize("template, expect", [
    ("{{ raise_exception('bad role') }}", "bad role"),
    ("{{ ''.__class__.__mro__ }}", "SecurityError"),  # unsafe attribute: blocked by the sandbox
    ("{{ messages.append(1) }}", "SecurityError"),  # inputs are immutable
    ("{% for i in range(100000) %}{{ 'x' * 20 }}{% endfor %}", "OutputLimit"),
    ("{% for x in %}", "TemplateSyntaxError"),
])
def test_failures_come_back_as_errors(sandbox, template, expect):
    r = sandbox.render(template, MSGS)
    assert not r.ok and expect in r.error


def test_timeout_kills_and_recovers(sandbox):
    slow = "{% for i in range(100000) %}{% for j in range(100000) %}{% endfor %}{% endfor %}"
    r = sandbox.render(slow, MSGS)
    assert not r.ok and r.error.startswith("Timeout")
    assert sandbox.render("{{ messages[0].content }}", MSGS).prompt == "hi"
    assert sandbox.restarts >= 1
