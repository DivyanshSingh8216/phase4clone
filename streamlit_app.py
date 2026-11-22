"""Streamlit Community Cloud entry point for the governed PulseIQ explorer."""
from __future__ import annotations
import hashlib, os, runpy, sys, tempfile
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import duckdb
import streamlit as st

ROOT=Path(__file__).resolve().parent
PACKAGE=ROOT/"phase4_complete"
sys.path.insert(0,str(PACKAGE))
os.environ["PULSEIQ_AUTH_MODE"]="production"

def secret(name: str) -> str:
    try: return str(st.secrets[name]).strip()
    except Exception: return ""

def install_hosted_warehouse() -> Path:
    target_dir=Path(tempfile.gettempdir())/"pulseiq_warehouse"
    target=target_dir/"pulseiq.duckdb"
    source_url=secret("PULSEIQ_DB_URL")
    expected=secret("PULSEIQ_DB_SHA256").lower()
    if not source_url or urlparse(source_url).scheme!="https":
        raise RuntimeError("PULSEIQ_DB_URL must be a private HTTPS object URL in Streamlit secrets.")
    if len(expected)!=64 or any(c not in "0123456789abcdef" for c in expected):
        raise RuntimeError("PULSEIQ_DB_SHA256 must be a valid 64-character SHA-256 checksum.")
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==expected:
        os.environ["PULSEIQ_DB_PATH"]=str(target)
        return target
    target_dir.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix="pulseiq-",suffix=".part",dir=target_dir)
    os.close(fd)
    tmp_path=Path(tmp)
    try:
        digest=hashlib.sha256()
        total=0
        request=Request(source_url,headers={"User-Agent":"PulseIQ-Streamlit/1.0"})
        with urlopen(request,timeout=90) as response,tmp_path.open("wb") as out:
            while True:
                chunk=response.read(1024*1024)
                if not chunk: break
                total+=len(chunk)
                if total>2*1024*1024*1024: raise RuntimeError("Warehouse exceeds the 2 GB deployment safety limit.")
                digest.update(chunk); out.write(chunk)
        if digest.hexdigest()!=expected: raise RuntimeError("Hosted warehouse checksum mismatch.")
        with duckdb.connect(str(tmp_path),read_only=True) as con:
            tables={r[0] for r in con.execute("SHOW TABLES").fetchall()}
            if not {"all_metrics","metric_catalog"}.issubset(tables):
                raise RuntimeError("Warehouse is missing all_metrics or metric_catalog.")
        tmp_path.replace(target)
    finally:
        if tmp_path.exists(): tmp_path.unlink()
    os.environ["PULSEIQ_DB_PATH"]=str(target)
    return target

st.title("PulseIQ | Secure sign-in")
if not st.user.is_logged_in:
    st.write("Sign in with your organisation-approved account to access governed PulseIQ metrics.")
    st.login()
    st.stop()
try:
    install_hosted_warehouse()
except Exception as exc:
    st.error(f"PulseIQ cannot load its approved hosted warehouse: {exc}")
    st.stop()
with st.sidebar:
    st.caption(f"Signed in as {st.user.email}")
    if st.button("Sign out"): st.logout()
try:
    runpy.run_path(str(PACKAGE/"explorer_v2.py"),run_name="__main__")
except Exception as exc:
    st.error(f"PulseIQ explorer could not start: {exc}")
    st.exception(exc)
