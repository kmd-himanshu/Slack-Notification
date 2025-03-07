#!/usr/bin/env python3
"""
Slack Notification - A simple module for sending Slack notifications
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SlackNotifier:
    """Class for sending notifications to Slack"""
    
    def __init__(self, webhook_url: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize the Slack notifier
        
        Args:
            webhook_url: Slack webhook URL (can be set via SLACK_WEBHOOK_URL env var)
            token: Slack API token (can be set via SLACK_API_TOKEN env var)
        """
        self.webhook_url = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
        self.token = token or os.getenv('SLACK_API_TOKEN')
        
        if not self.webhook_url and not self.token:
            logger.warning("No Slack credentials provided. Please set SLACK_WEBHOOK_URL or SLACK_API_TOKEN")
    
    def send_webhook_message(self, 
                            text: str, 
                            channel: Optional[str] = None,
                            username: Optional[str] = None,
                            attachments: Optional[List[Dict]] = None) -> Dict:
        """
        Send a message using Slack webhook
        
        Args:
            text: Message text
            channel: Channel to send to (if webhook supports it)
            username: Username to use (if webhook supports it)
            attachments: List of attachment dictionaries
            
        Returns:
            Response from Slack API
        """
        if not self.webhook_url:
            raise ValueError("Webhook URL is required")
        
        payload = {"text": text}
        
        if channel:
            payload["channel"] = channel
        if username:
            payload["username"] = username
        if attachments:
            payload["attachments"] = attachments
            
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return {"success": True, "status_code": response.status_code}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Slack webhook message: {e}")
            return {"success": False, "error": str(e)}
    
    def send_api_message(self,
                        text: str,
                        channel: str,
                        attachments: Optional[List[Dict]] = None,
                        blocks: Optional[List[Dict]] = None) -> Dict:
        """
        Send a message using Slack API
        
        Args:
            text: Message text
            channel: Channel ID or name to send to
            attachments: List of attachment dictionaries
            blocks: List of block dictionaries
            
        Returns:
            Response from Slack API
        """
        if not self.token:
            raise ValueError("Slack API token is required")
        
        payload = {
            "text": text,
            "channel": channel
        }
        
        if attachments:
            payload["attachments"] = attachments
        if blocks:
            payload["blocks"] = blocks
            
        try:
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                json=payload,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {self.token}"
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Slack API message: {e}")
            return {"success": False, "error": str(e)}


def main():
    """Example usage"""
    # Example with webhook
    notifier = SlackNotifier(webhook_url=os.getenv('SLACK_WEBHOOK_URL'))
    
    # Simple message
    result = notifier.send_webhook_message(
        text="Hello from Slack Notification!",
        username="NotificationBot"
    )
    print(f"Webhook result: {result}")
    
    # Example with API token
    if os.getenv('SLACK_API_TOKEN'):
        api_notifier = SlackNotifier(token=os.getenv('SLACK_API_TOKEN'))
        api_result = api_notifier.send_api_message(
            text="Hello from Slack API!",
            channel="#general"
        )
        print(f"API result: {api_result}")


if __name__ == "__main__":
    main()