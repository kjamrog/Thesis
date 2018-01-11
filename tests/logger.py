import unittest
import src.logger as logging

class LoggerTests(unittest.TestCase):
    
    def test_setup(self):
        ''' Saves logs to file run.log '''
        logs_file = 'run.log'
        logging.setup()
        with open(logs_file) as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 0)
        logger = logging.get_logger()
        logger.info('info_message')
        logger.error('error_message')
        with open(logs_file) as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertTrue('[INFO]' in lines[0])
            self.assertTrue('info_message' in lines[0])
            self.assertTrue('[ERROR]' in lines[1])
            self.assertTrue('error_message' in lines[1])
