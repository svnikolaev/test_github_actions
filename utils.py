from pathlib import Path
from typing import Optional
import subprocess


def via_run_service(BASEDIR: Path,
                    service_name: str,
                    args: Optional[str] = 'nvt') -> None:
    ''' args = '-nvt'  # no create logfile, verbose, testing '''
    run_service = BASEDIR.joinpath('run_service.py')
    print(f'TEST RUN of service "{service_name}" with args "{args}":\n')
    subprocess.call(['python', run_service, f'-{args}', service_name])
    print('\nTEST RUN finished')
