import contextlib
import subprocess  # noqa: F401
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from pathlib import Path
import requests  # type: ignore

import zipfile
import os


@contextlib.contextmanager
def CD(d: str):
    import os

    old = os.getcwd()
    os.chdir(d)
    yield
    os.chdir(old)


def build_wheel():
    pass


def download_nginx(save_path: Path):
    try:
        response = requests.get(
            'https://nginx.org/download/nginx-1.27.5.zip', stream=True
        )
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'File downloaded successfully to: {save_path}')

    except requests.exceptions.RequestException as e:
        print(f'An error occurred during the download: {e}')
        exit(-1)
    except IOError as e:
        print(f'An error occurred during file saving: {e}')
        exit(-1)


def unzip_archive(zip_file_path, extract_to_dir):
    """
    Unzips an entire archive to a specified directory.

    Args:
        zip_file_path (str): The path to the zip file.
        extract_to_dir (str): The directory where contents will be extracted.
    """
    # Ensure the extraction directory exists
    os.makedirs(extract_to_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            print(
                f"Extracting all contents of '{zip_file_path}' to '{extract_to_dir}'..."
            )
            zip_ref.extractall(extract_to_dir)
            print('Extraction complete!')
    except FileNotFoundError:
        print(f"Error: Zip file not found at '{zip_file_path}'")
    except zipfile.BadZipFile:
        print(f"Error: '{zip_file_path}' is not a valid zip file or is corrupted.")
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def extract_nginx(save_path: Path):
    unzip_archive(save_path, save_path.parent)


def move_nginx(src: Path, dst: Path):
    import shutil

    for i in os.listdir(src):
        item = src.joinpath(i)
        shutil.move(item, dst)


def build_sdist():
    cwd = Path(__file__).resolve().parent
    save_path = cwd.joinpath('soda_nginx_bin/nginx.zip')
    if save_path.exists():
        pass
    else:
        download_nginx(save_path)

    bin_path = cwd.joinpath('soda_nginx_bin')
    if not bin_path.joinpath('nginx-1.27.5').exists():
        extract_nginx(save_path)

    if not bin_path.joinpath('nginx.exe').exists():
        move_nginx(bin_path.joinpath('nginx-1.27.5'), bin_path)


class CustomBuilder(BuildHookInterface):
    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, Any],
    ) -> None:
        build_data['tag'] = 'py3-none-win_amd64'
        if self.target_name == 'sdist':
            build_sdist()
        else:
            build_wheel()


if __name__ == '__main__':
    build_wheel()
