import logging
from datetime import datetime
import json

class CallLogHandler(logging.Handler):
    """Custom log handler for call events"""
    
    def emit(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # In production, send to monitoring service
        print(json.dumps(log_entry))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Add custom handler for call events
    call_logger = logging.getLogger("call_events")
    call_logger.addHandler(CallLogHandler())
    
    return call_logger