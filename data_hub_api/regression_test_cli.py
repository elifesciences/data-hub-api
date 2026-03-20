import argparse
import os
import sys

import pytest


DEFAULT_URL_PREFIX = 'http://localhost:8000'
URL_PREFIX_ENV = 'DATA_HUB_API_REGRESSION_TEST_URL_PREFIX'

SUITE_PATHS = {
    'all': 'tests/regression_tests',
    'docmaps': 'tests/regression_tests/docmaps',
    'kotahi': 'tests/regression_tests/kotahi_docmaps',
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Run regression tests against the Data Hub API'
    )
    parser.add_argument(
        '--url-prefix',
        default=os.getenv(URL_PREFIX_ENV, DEFAULT_URL_PREFIX),
        help=(
            f'URL prefix for the API under test '
            f'(env: {URL_PREFIX_ENV}, default: {DEFAULT_URL_PREFIX})'
        )
    )
    parser.add_argument(
        '--suite',
        choices=list(SUITE_PATHS.keys()),
        default='all',
        help='Which regression test suite to run (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose pytest output'
    )
    args = parser.parse_args()

    os.environ[URL_PREFIX_ENV] = args.url_prefix

    pytest_args = ['-p', 'no:cacheprovider', SUITE_PATHS[args.suite]]
    if args.verbose:
        pytest_args = ['-vv'] + pytest_args

    sys.exit(pytest.main(pytest_args))


if __name__ == '__main__':
    main()
