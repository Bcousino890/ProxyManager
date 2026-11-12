import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import time

import pytest


@pytest.mark.skipif(shutil.which("sqlite3") is None, reason="sqlite3 CLI no instalado")
def test_backup_is_consistent_private_and_rotated(tmp_path):
    db_path = tmp_path / "live.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE marker (value TEXT)")
        db.execute("INSERT INTO marker VALUES ('saved')")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir(mode=0o700)
    old = backup_dir / "proxymanager-old.sqlite3"
    old.write_bytes(b"old")
    old_time = time.time() - 10 * 86400
    os.utime(old, (old_time, old_time))

    script = Path(__file__).resolve().parents[1] / "scripts" / "backup.sh"
    run = subprocess.run(["bash", str(script), str(db_path), str(backup_dir), "7"], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    assert "Fernet" not in script.read_text()
    assert not old.exists()
    backups = list(backup_dir.glob("proxymanager-*.sqlite3"))
    assert len(backups) == 1
    assert (backups[0].stat().st_mode & 0o777) == 0o600
    assert (backup_dir.stat().st_mode & 0o777) == 0o700
    with sqlite3.connect(backups[0]) as db:
        assert db.execute("SELECT value FROM marker").fetchone() == ("saved",)
    assert str(backups[0]) in run.stdout
