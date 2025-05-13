from sodatools import Path, CD, str_path
import subprocess
import sys
import os

CR = Path(__file__).parent
bindir = CR.parent.joinpath('soda_nginx_bin')


def init_config():
    cwd = Path(os.getcwd())
    sys.path.insert(0, str_path(cwd))
    try:
        from nginx_config import get_config  # type: ignore
    except ImportError as e:
        print('cannot find config', e)
        exit(-1)

    config = get_config()
    bindir.joinpath('conf/nginx.conf').write_text(encoding='utf8', data=config)

    bindir.joinpath('logs').mkdir(exist_ok=True)
    bindir.joinpath('temp/client_body_temp').mkdir(exist_ok=True, parents=True)
    bindir.joinpath('temp/proxy_temp').mkdir(exist_ok=True, parents=True)
    bindir.joinpath('temp/fastcgi_temp').mkdir(exist_ok=True, parents=True)
    bindir.joinpath('temp/scgi_temp').mkdir(exist_ok=True, parents=True)
    bindir.joinpath('temp/uwsgi_temp').mkdir(exist_ok=True, parents=True)


def main():
    if len(sys.argv) == 1:
        init_config()
        # sys.argv.extend(["-g", "daemon off; error_log stderr info;"])
    with CD(bindir):
        args = [bindir / 'nginx.exe']
        args.extend(sys.argv[1:])
        try:
            subprocess.run(args, check=False)
        except KeyboardInterrupt:
            return


if __name__ == '__main__':
    main()
