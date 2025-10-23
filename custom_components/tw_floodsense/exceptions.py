"""Custom exceptions for TWFloodSense integration."""

class TWFloodSenseError(Exception):
    """Base exception for TWFloodSense errors"""
    def __init__(self, detail: dict = None):
        super().__init__(detail)
        self.detail = detail or {}

    def __getitem__(self, key):
        return self.detail.get(key)

    def __str__(self):
        return f"{self.__class__.__name__}({self.detail})"


class ApiAuthError(TWFloodSenseError):
    """API authentication failed"""
    

class DataNotFoundError(TWFloodSenseError):
    """No valid data found in the API response"""


class RecordNotFoundError(TWFloodSenseError):
    """No records found in the API response"""


class UnexpectedStatusError(TWFloodSenseError):
    """API returned unexpected status code"""


class RequestTimeoutError(TWFloodSenseError):
    """Request timed out"""


class RequestFailedError(TWFloodSenseError):
    """Request failed"""
