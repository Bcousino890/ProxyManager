import subprocess
import sys

from proxymanager.config import Settings
from proxymanager.doctor import diagnose


def test_doctor_flags_missing_config(tmp_path):
    levels = dict((m, l) for l, m in diagnose(Settings(db_path=str(tmp_path / "d.db"))))
    assert any(l == "ERROR" and "ADMIN_KEY" in m for m, l in levels.items())
    assert any(l == "ERROR" and "CREDENTIAL_KEY" in m for m, l in levels.items())


def test_doctor_ok_with_good_config(tmp_path):
    from cryptography.fernet import Fernet
    s = Settings(db_path=str(tmp_path / "d.db"), admin_key="a" * 32, credential_key=Fernet.generate_key().decode(), support_email="a@b.co")
    assert not [m for l, m in diagnose(s) if l == "ERROR"]
    assert "a" * 32 not in str(diagnose(s))


def test_handlercheck_runs_template(tmp_path):
    page = tmp_path / "p.html"
    page.write_text("captcha")
    out = subprocess.run([sys.executable, "-m", "proxymanager.handlercheck", "examples.handler_template:TemplateHandler", "--html", str(page)], capture_output=True, text=True, cwd=".", env={"PYTHONPATH": "."})
    assert out.returncode == 0 and "None" in out.stdout, out.stderr
