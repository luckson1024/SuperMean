# SelfImprovementLogger: Logs all self-improvement actions for audit/rollback
import logging
import datetime
import json

class SelfImprovementLogger:
    def __init__(self, logfile='logs/self_improvement.log'):
        self.logfile = logfile
        self.logger = logging.getLogger('SelfImprovementLogger')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.logfile)
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def log_action(self, action_type, details):
        entry = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'action_type': action_type,
            'details': details
        }
        self.logger.info(json.dumps(entry))

    def get_logs(self):
        with open(self.logfile) as f:
            return f.readlines()
