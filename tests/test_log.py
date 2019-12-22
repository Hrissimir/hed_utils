import logging
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, mock

from hed_utils.support import log


class LogTest(TestCase):

    def test_add_file_handler(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file_path = Path(tmp_dir).joinpath("my_output.log")
            log_level = logging.INFO
            logger = logging.getLogger("test_file_handler")
            self.assertFalse(log_file_path.exists())
            log.add_file_handler(logger, str(log_file_path), log_level)
            included_msg = "im here"
            logger.info(included_msg)
            self.assertIn(included_msg, log_file_path.read_text())
            excluded_msg = "im not"
            logger.debug(excluded_msg)
            self.assertNotIn(excluded_msg, log_file_path.read_text())

    def test_init(self):
        loglevel = logging.ERROR
        logfmt = log.LOG_FORMAT
        mock_cfg_func = mock.Mock()
        logging.basicConfig = mock_cfg_func

        with tempfile.TemporaryDirectory() as tmp_dir:
            logfile = Path(tmp_dir).joinpath("my_output.log")

            with mock.patch("hed_utils.support.log.add_file_handler") as mock_add_hdlr:
                log.init(loglevel, logfmt, True, logfile)
                log.init(loglevel, logfmt, False)

                mock_add_hdlr.assert_called_once_with(logging.getLogger(), logfile, loglevel, logfmt)

                expected_cfg_calls = [
                    mock.call(level=loglevel, format=logfmt, stream=sys.stdout),
                    mock.call(level=loglevel, format=logfmt)
                ]

                actual_cfg_calls = mock_cfg_func.mock_calls
                self.assertListEqual(expected_cfg_calls, actual_cfg_calls)
