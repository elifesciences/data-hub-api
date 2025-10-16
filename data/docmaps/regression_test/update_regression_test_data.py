import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def main():
    LOGGER.info('Updating regression test data...')
    docmap_by_manuscript_id_data_path = (
        Path('./data/docmaps/regression_test/docmap_by_manuscript_id')
    )
    json_files = list(docmap_by_manuscript_id_data_path.glob('*.json'))
    LOGGER.info('Found %d JSON files:', len(json_files))
    for json_file in json_files:
        LOGGER.info('JSON file: %s', json_file)
        manuscript_id = Path(json_file).name.split('.')[0]
        LOGGER.info('manuscript_id: %s', manuscript_id)
    LOGGER.info('Regression test data updated.')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
