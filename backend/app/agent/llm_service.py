import aiohttp
from typing import Dict, List, Any, Optional
import json
import os
import re
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        self.api_key = api_key
        self.model = model
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.headers = {
            "Content-Type": "application/json"
        }
        logger.info(f"LLM Service initialized with model: {model}")
    
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, json.JSONDecodeError)),
        reraise=True
    )
    async def generate_text(self, prompt: str) -> str:
        """Generate text from the Gemini model"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 1000
                    }
                }
                
                url = f"{self.endpoint}?key={self.api_key}"
                logger.info(f"Sending request to LLM API endpoint")
                
                async with session.post(url, headers=self.headers, json=payload, timeout=30) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        error_msg = f"LLM API error: {response.status} - {error_text}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    data = await response.json()
                    
                    # Extract text from Gemini's response format
                    try:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    except (KeyError, IndexError) as e:
                        error_msg = f"Unexpected response format: {e}, Response: {data}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Error in generate_text: {str(e)}")
            raise
    
    async def get_tool_decision(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get a tool decision from the LLM"""
        # Add specific instructions for JSON output to the prompt
        structured_prompt = f"""{prompt}

Please respond with a valid JSON object that follows this structure:
- If a tool should be used:
{{
  "tool_name": "the-name-of-the-tool-to-use",
  "inputs": {{
    "param1": "value1", 
    "param2": "value2"
  }}
}}

- If no tool should be used:
{{
  "no_tool": true,
  "reason": "explanation why no tool is needed"
}}
"""
        
        try:
            response = await self.generate_text(structured_prompt)
            
            # Extract JSON from the response
            return self._extract_json_from_response(response)
        except Exception as e:
            logger.error(f"Error parsing tool decision: {e}")
            logger.error(f"Response: {response if 'response' in locals() else 'No response received'}")
            return None
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from a text response"""
        # Find JSON pattern in the response
        json_match = re.search(r'({[\s\S]*})', response)
        if not json_match:
            error_msg = "No JSON found in response"
            logger.error(f"{error_msg}: {response}")
            raise ValueError(error_msg)
        
        json_str = json_match.group(1)
        
        # Try to parse the JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to clean up the JSON string
            # Remove markdown code block syntax
            json_str = re.sub(r'```json|```', '', json_str).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}, Response: {response}")
                raise 