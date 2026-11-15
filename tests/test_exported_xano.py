"""Static checks for the deployment subset; not a Xano compiler or remote test."""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
DEPLOY=ROOT/'xano/deploy'


def test_all_fifteen_operations_guard_before_database_access():
    endpoints=list((DEPLOY/'api/edutrack_teste').rglob('*.xs'))
    assert len(endpoints)==15
    for path in endpoints:
        source=path.read_text()
        assert source.count('function.run "auth/validate_api_key"')==1
        assert source.index('function.run "auth/validate_api_key"') < source.index('db.')
        assert re.search(r'guid = "[^"]+"',source)


def test_patch_limits_mutable_fields_without_dropping_explicit_null():
    for path in DEPLOY.rglob('*PATCH.xs'):
        source=path.read_text()
        assert '|filter_null' not in source
        assert '|filter_empty_text' not in source
        assert '$raw_input|keys' in source
        expression=next(line for line in source.splitlines() if 'data =' in line)
        assert '|pick:[' in expression
        assert '"id"' not in expression and '"created_at"' not in expression


def test_package_excludes_unrelated_objects_and_secrets():
    paths=list(DEPLOY.rglob('*.xs'))
    assert len(paths)==16
    for path in paths:
        source=path.read_text()
        assert 'swagger' not in source and 'access_token' not in source
        assert not re.search(r'^\s*(table|workspace|api_group)\s+[^=]',source,re.M)
    guard=(DEPLOY/'function/auth/validate_api_key.xs').read_text()
    assert '$env.XANO_API_KEY' in guard
    assert 'error_type = "accessdenied"' in guard
