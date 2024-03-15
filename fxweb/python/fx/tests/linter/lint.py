#!/usr/bin/env python3

import inspect
import os
import subprocess
import sys
from argparse import ArgumentParser

import pkg_resources
from colorama import Fore
from colorama import init as colorama_init


def check_dependencies(script_dir):
    def format_line(package, status):
        pretty_status = ""
        if status == "Installed":
            pretty_status = f"{Fore.GREEN}{status}"
        elif status in ["Missing", "Outdated"]:
            pretty_status = f"{Fore.RED}{status}"
        else:
            pretty_status = status

        return f"{package}".ljust(15) + f"{pretty_status}".rjust(15)

    print("Checking dependencies...\n")

    missing_packages = 0
    with open(script_dir + "/requirements.lint.txt", "r") as file_data:
        requirements = file_data.read().splitlines()

        for requirement in requirements:
            try:
                package = requirement.split("==")[0]
                pkg_resources.require(requirement)
                status = "Installed"

            except pkg_resources.DistributionNotFound:
                status = "Missing"
                missing_packages += 1

            except pkg_resources.VersionConflict:
                status = "Outdated"
                missing_packages += 1

            finally:
                print(format_line(package, status))

    if missing_packages:
        sys.exit(1)


def execute_command(cmd, ignore_error=False):
    cmd = " ".join(cmd)
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"{Fore.GREEN}Test passed")

    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Test failed")
        if not ignore_error:
            sys.exit(e.returncode)


def modified_files(branch):
    result = subprocess.check_output(
        ["git", "diff", "--name-only", branch, "--", "fx/application/kmes"]
    ).decode()
    files = []
    for file_name in result.split("\n"):
        if not file_name:
            continue

        if os.path.isfile(file_name):
            files.append(file_name)

    return files


if __name__ == "__main__":
    # This script depends on config files in this directory
    script_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    # Base project directory
    os.chdir(script_dir + "/../../..")

    parser = ArgumentParser(description="Python Linter")
    parser.add_argument("-b", "--branch", required=True, help="Git branch to compare against")
    parser.add_argument("-f", "--fix", action="store_true", help="Fix instead of creating a diff")
    parser.add_argument(
        "-i", "--ignore-dependencies", action="store_true", help="Ignore package dependencies"
    )

    options = parser.parse_args()
    files = modified_files(options.branch)
    if not files:
        print("\nNo files to check")
        exit(0)

    # Lint ourselves too
    files.append(script_dir + "/lint.py")
    colorama_init(autoreset=True)

    if options.ignore_dependencies:
        print("\nIgnoring Dependencies")
    else:
        check_dependencies(script_dir)

    print("\nRunning flake8 linter...")
    # Flake8 doesn't have an ability to autofix
    # TODO autopep8 might be a solution to this
    execute_command(
        ["flake8", "--config", script_dir + "/.flake8"] + files, ignore_error=options.fix
    )

    print("\nRunning Black linter...")
    black_extra = [] if options.fix else ["--check", "--diff"]
    execute_command(
        ["black", "--color", "--target-version", "py36", "--line-length", "100"]
        + black_extra
        + files,
        ignore_error=options.fix,
    )

    print("\nRunning isort linter...")
    isort_extra = [] if options.fix else ["--check", "--diff"]
    execute_command(
        ["isort", "--settings-path", script_dir + "/.fx_web.toml"] + isort_extra + files,
        ignore_error=options.fix,
    )
