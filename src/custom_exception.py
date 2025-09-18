import sys

class CustomException(Exception):
    def __init__(self, message: str, error_detail: Exception = None):
        self.error_message = self.get_detailed_error_message(message, error_detail)
        super().__init__(self.error_message)
        
    @staticmethod
    def get_detailed_error_message(message: str, error_detail: Exception = None):
        if error_detail:
            return f"{message} : {str(error_detail)}"
        return message
    
    def __str__(self):
        return self.error_message