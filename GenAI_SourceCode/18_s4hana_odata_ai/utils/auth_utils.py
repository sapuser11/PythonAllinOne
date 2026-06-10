import base64
import requests
from typing import Dict, Optional
from utils.config import Config
from utils.logger_utils import setup_logger
import json

logger = setup_logger(__name__)

class SAPAuth:
    def __init__(self):
        self.username = Config.SAP_USERNAME
        self.password = Config.SAP_PASSWORD
        self.client = Config.SAP_CLIENT
        self.base_url = Config.SAP_BASE_URL
        self.session = requests.Session()
        self.csrf_token = None
        
    def get_basic_auth_header(self) -> Dict[str, str]:
        """Generate basic authentication header for SAP"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "sap-client": self.client,
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    
    def get_csrf_token_and_cookies(self) -> Optional[str]:
        """Get CSRF token and establish session cookies like Postman"""
        try:
            # Clear any existing cookies
            self.session.cookies.clear()
            
            headers = {
                "Authorization": f"Basic {base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()}",
                "x-csrf-token": "fetch",
                "Accept": "application/json",
                "sap-client": self.client
            }
            
            logger.info("Getting CSRF token and establishing session...")
            response = self.session.get(
                f"{self.base_url}{Config.SAP_API_PATH}",
                headers=headers,
                timeout=30
            )
            
            logger.info(f"CSRF response status: {response.status_code}")
            logger.info(f"CSRF response headers: {dict(response.headers)}")
            logger.info(f"Session cookies after CSRF: {dict(self.session.cookies)}")
            
            if response.status_code in [200, 404]:
                csrf_token = response.headers.get("x-csrf-token")
                if csrf_token:
                    self.csrf_token = csrf_token
                    logger.info(f"✅ CSRF token obtained: {csrf_token[:10]}...")
                    logger.info(f"✅ Session cookies established: {len(self.session.cookies)} cookies")
                    
                    # Log cookie details
                    for cookie in self.session.cookies:
                        logger.info(f"Cookie: {cookie.name}={cookie.value[:50]}...")
                    
                    return csrf_token
                else:
                    logger.error("CSRF token not found in response headers")
                    return None
            else:
                logger.error(f"Failed to get CSRF token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting CSRF token: {str(e)}")
            return None
    
    def make_sap_request(self, url: str, payload: dict) -> requests.Response:
        """Make SAP request using established session and cookies"""
        if not self.csrf_token:
            raise Exception("CSRF token not available. Call get_csrf_token_and_cookies first.")
        
        # Use minimal headers like Postman - let requests handle cookies automatically
        headers = {
            "x-csrf-token": self.csrf_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()}"
        }
        
        logger.info("Making SAP request with established session...")
        logger.info(f"Using {len(self.session.cookies)} session cookies")
        logger.info(f"Request headers: {json.dumps({k: v for k, v in headers.items() if k != 'Authorization'}, indent=2)}")
        
        # Let the session handle cookies automatically
        response = self.session.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        return response
    