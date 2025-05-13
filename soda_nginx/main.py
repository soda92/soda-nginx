from sodatools import Path, CD
import subprocess
import sys


def main():
    cwd = Path(__file__).parent
    bindir = cwd.parent.joinpath('soda_nginx_bin')
    with CD(bindir):
        args = [bindir / 'nginx.exe']
        args.extend(sys.argv[1:])
        subprocess.run(args, check=True)


if __name__ == '__main__':
    main()
