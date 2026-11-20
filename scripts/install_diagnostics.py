#!/usr/bin/env python3
"""Privacy-conscious offline end-user installation checks; stdlib-only driver.

Run from the installed skill. No network, no birth data, no usernames/paths in report.
With --require-astronomy, missing optional dependencies become a failure.
This is a local diagnosis, NOT proof of installation on another person's PC.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
sys.path.insert(0, str(Path(__file__).resolve().parent))
from swiss_compat import installed_binding, calc_ut as compat_calc_ut

ROOT=Path(__file__).resolve().parents[1]

def run_script(*relative_args,timeout=25):
    try:
        # Child JSON must not inherit Windows PowerShell 5.1's non-UTF8 pipe encoding.
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        completed=subprocess.run([sys.executable,str(ROOT/'scripts'/relative_args[0]),*relative_args[1:]],
                                 cwd=str(ROOT),capture_output=True,encoding='utf-8',
                                 errors='strict',env=env,timeout=timeout)
        if completed.returncode!=0:
            return False,f'returncode={completed.returncode}'
        try:
            parsed=json.loads(completed.stdout)
            return True,parsed
        except json.JSONDecodeError:
            return False,'command did not return valid JSON'
    except (OSError,subprocess.TimeoutExpired) as exc:
        return False, type(exc).__name__

def diagnose(require_astronomy=False, installed=False):
    checks=[]
    def append(name,ok,detail=None,skipped=False):
        checks.append({'check':name,'status':'SKIP' if skipped else ('PASS' if ok else 'FAIL'),
                       'detail':detail if isinstance(detail,str) else None})
    append('SKILL.md and catalogs', all((ROOT/p).exists() for p in ('SKILL.md','data/tarot.json','data/iching.json')))
    append('Python >=3.10',sys.version_info>=(3,10),f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')
    try:
        ZoneInfo('Asia/Shanghai');ZoneInfo('America/New_York')
        append('IANA time zone data',True)
    except ZoneInfoNotFoundError:
        append('IANA time zone data',False,'Install tzdata or repair OS timezone database')
    if installed:
        home=Path.home()
        actual=(home/'.codex'/'skills'/'symbolic-reflection-support'/'SKILL.md')
        append('Codex skill path', actual.is_file(), 'Expected .codex/skills/symbolic-reflection-support/SKILL.md (path redacted)')
    ok,payload=run_script('draw.py','tarot','--count','1','--seed','2026')
    append('deterministic Tarot command',ok and isinstance(payload,dict))
    ok,payload=run_script('draw.py','iching','--lines','7','8','7','9','7','8')
    append('known I Ching 49->63 fixture',ok and payload.get('primary',{}).get('number')==49 and payload.get('resulting',{}).get('number')==63)
    try:
        import swisseph as sw
        binding=installed_binding()
        if binding['name']=='unknown':
            raise RuntimeError('Swiss binding package distribution not identified')
        pos,flags,msg=compat_calc_ut(sw,sw.julday(2000,1,1,12),sw.MOON,sw.FLG_MOSEPH)
        append('Swiss binding import and calc_ut ABI',True,
               f"distribution={binding['name']} {binding['version']}; backend={sw.version}")
        astro=True
    except (ImportError,RuntimeError,ValueError,AttributeError) as exc:
        append('Swiss binding import and calc_ut ABI',not require_astronomy,
               f'optional extra not ready: {type(exc).__name__}',skipped=not require_astronomy)
        astro=False
    if astro:
        ok,payload=run_script('natal.py','--datetime','2000-01-01T12:00:00','--tz','Europe/London',
                              '--lat','51.4779','--lon','0','--houses','placidus',timeout=20)
        append('public neutral natal chart',ok and payload.get('kind')=='tropical_natal_chart_calculation')
        ok,payload=run_script('bazi.py','--datetime','2024-02-10T12:00:00','--tz','Asia/Shanghai',
                              '--lat','39.9042','--lon','116.4074',timeout=25)
        append('public neutral BaZi chart',ok and payload.get('kind')=='bazi_calculation')
        ok,payload=run_script('verify_ephemeris.py','--strict',timeout=30)
        append('independent model QA 6 epochs',ok and payload.get('status')=='PASS_MODEL_LEVEL'
               and payload.get('measurements')==66)
    else:
        for name in ('public neutral natal chart','public neutral BaZi chart','independent model QA 6 epochs'):
            append(name,False,'optional astronomy dependency not available',skipped=not require_astronomy)
    state='PASS' if not any(c['status']=='FAIL' for c in checks) else 'FAIL'
    return {'schema_version':'1.3.5','kind':'local_install_diagnostics',
            'generated_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'status':state,'platform':platform.system(), 'python':platform.python_version(),
            'privacy_note':'No birth data, usernames, hostnames, file paths or IP addresses are collected; report remains local unless you share it.',
            'checks':checks,'passes':sum(c['status']=='PASS' for c in checks),
            'failures':sum(c['status']=='FAIL' for c in checks),'skipped':sum(c['status']=='SKIP' for c in checks),
            'limits':'A successful run in this environment does not establish that a different user’s Windows/Codex installation works.'}

def main():
    p=argparse.ArgumentParser(description='Local, privacy-conscious installation report')
    p.add_argument('--require-astronomy',action='store_true')
    p.add_argument('--installed',action='store_true',help='Check Codex path in this user profile')
    p.add_argument('--report',help='Optional path to save JSON report')
    a=p.parse_args()
    report=diagnose(a.require_astronomy,a.installed)
    output=json.dumps(report,ensure_ascii=False,indent=2)
    print(output)
    if a.report:Path(a.report).write_text(output+'\n',encoding='utf-8')
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
