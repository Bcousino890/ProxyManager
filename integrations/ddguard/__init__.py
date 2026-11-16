"""ddguard: DataDome handling for Idealista (HTTP first, browser only to clear a challenge)."""
from .detect import Verdict, classify
from .session import Blocked, DDPool, DDSession, Page
from .solver import BrowserSolver, SolveFailed
from .store import SessionStore

__all__ = ["DDSession", "DDPool", "Page", "Blocked", "BrowserSolver", "SolveFailed",
           "SessionStore", "Verdict", "classify"]
__version__ = "0.1.0"
