import os
from dotenv import load_dotenv
import logging
import sys
import requests
import json

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        try:
            # Load environment variables
            load_dotenv(override=True)
            
            # Get API key
            self.api_key = os.getenv('GEMINI_API_KEY')
            logger.debug(f"API Key found: {'Yes' if self.api_key else 'No'}")
            
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            # Set up API endpoint
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
            
            # Test the API connection
            self._test_connection()
            
            logger.info("GeminiService initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing GeminiService: {str(e)}", exc_info=True)
            raise
    
    def _test_connection(self):
        """Test the API connection with a simple prompt"""
        try:
            logger.debug("Testing API connection...")
            response = self._make_api_request("Test connection")
            if response and 'text' in response:
                logger.info("API connection test successful")
                logger.debug(f"Test response: {response['text'][:100]}...")
            else:
                raise Exception("Empty response from API")
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}", exc_info=True)
            raise
    
    def _make_api_request(self, prompt):
        """Make a request to the Gemini API"""
        headers = {
            'Content-Type': 'application/json'
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return {
                    'text': result['candidates'][0]['content']['parts'][0]['text']
                }
            else:
                raise Exception("No valid response in API result")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}", exc_info=True)
            raise
    
    def get_loan_advice(self, input_data, eligibility, probability, reasons):
        """Get AI-powered loan advice based on the application details"""
        
        prompt = f"""
        As a financial advisor, analyze this loan application and provide detailed advice:
        
        Applicant Details:
        - Age: {input_data['age']}
        - Annual Income: ₹{input_data['income']:,.2f}
        - Years of Employment: {input_data['employment_years']}
        - Credit Score: {input_data['credit_score']}
        - Loan Amount: ₹{input_data['loan_amount']:,.2f}
        - Down Payment: ₹{input_data['down_payment']:,.2f}
        - Debt-to-Income Ratio: {input_data['debt_to_income']}%
        - Loan Term: {input_data['loan_term']} years
        
        Eligibility Result:
        - Eligible: {eligibility}
        - Confidence Score: {probability:.1f}%
        
        Analysis Reasons:
        {chr(10).join(f'- {reason}' for reason in reasons)}
        
        Please provide:
        1. A detailed analysis of the application
        2. Specific recommendations for improvement if not eligible
        3. Financial advice regarding the loan terms
        4. Potential risks and considerations
        5. Alternative options if applicable
        
        Format the response in clear sections with bullet points where appropriate.
        """
        
        try:
            logger.debug("Requesting loan advice from Gemini")
            logger.debug(f"Prompt: {prompt[:200]}...")
            
            response = self._make_api_request(prompt)
            
            if response and 'text' in response:
                logger.info("Successfully received loan advice")
                logger.debug(f"Response preview: {response['text'][:200]}...")
                return response['text']
            else:
                raise Exception("Empty response from API")
        except Exception as e:
            logger.error(f"Error getting loan advice: {str(e)}", exc_info=True)
            return f"Error getting AI advice: {str(e)}"
    
    def get_financial_education(self, topic):
        """Get educational content about financial topics"""
        
        prompt = f"""
        As a financial educator, provide clear and concise information about: {topic}
        
        Please include:
        1. Basic explanation
        2. Key points to remember
        3. Common mistakes to avoid
        4. Best practices
        5. Additional resources
        
        Format the response in a clear, easy-to-understand manner with bullet points where appropriate.
        """
        
        try:
            logger.debug(f"Requesting financial education about: {topic}")
            logger.debug(f"Prompt: {prompt[:200]}...")
            
            response = self._make_api_request(prompt)
            
            if response and 'text' in response:
                logger.info("Successfully received financial education content")
                logger.debug(f"Response preview: {response['text'][:200]}...")
                return response['text']
            else:
                raise Exception("Empty response from API")
        except Exception as e:
            logger.error(f"Error getting financial education: {str(e)}", exc_info=True)
            return f"Error getting educational content: {str(e)}" 