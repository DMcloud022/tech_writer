import os
import logging
import traceback
import json
from groq import Groq
from typing import Dict, Any, Optional
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIPrompt:
    def __init__(self):
        try:
            self.groq_api_key = os.getenv("GROQ_API_KEY")
            self.serper_api_key = os.getenv("SERPER_API_KEY")
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set.")
            if not self.serper_api_key:
                raise ValueError("SERPER_API_KEY environment variable is not set.")
            self.client = Groq(api_key=self.groq_api_key)
            logger.info("Groq client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            raise

    def sanitize_input(self, text: str, max_length: int = 3000) -> str:
        """Sanitize and truncate input text."""
        return ' '.join(text.strip().split())[:max_length]

    def fetch_serper_results(self, query: str) -> Dict[str, Any]:
        """Fetch search results using Serper API."""
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        data = json.dumps({"q": query})

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Serper API request failed: {str(e)}")
            return {}

    def generate_prompt(self, content: str, approach: str, purpose: str, category: str, 
                        additional_params: Optional[Dict[str, Any]] = None) -> str:
        try:
            sanitized_content = self.sanitize_input(content)
            sanitized_approach = self.sanitize_input(approach)
            sanitized_purpose = self.sanitize_input(purpose)
            sanitized_category = self.sanitize_input(category)
            
            # Fetch relevant search results
            search_query = f"{sanitized_category} {sanitized_purpose}"
            search_results = self.fetch_serper_results(search_query)
            
            relevant_info = ""
            if (search_results and 'organic' in search_results):
                for result in search_results['organic'][:3]:  # Use top 3 results
                    relevant_info += f"\n- {result['title']}: {result['snippet']}"
            
            prompt = f"""

            As a senior technical writer and business analyst, please create a professional and standards-compliant technical report based on the provided text {sanitized_content}.

            Writing Approach: Incorporate the specified writing approach {sanitized_approach} to ensure consistency and clarity throughout the report.
            Purpose: The report's purpose is {sanitized_purpose} and it is intended for an audience related to {sanitized_category}.
            Standards and Format: Adhere to industry standards for technical writing, including typical report formats and structures. 
            Use clear, concise language, and ensure the report is error-free, easy to understand, and visually appealing.
            Additionally, provide a detailed analysis of the relevant information from recent search results, {relevant_info}. 
            Summarize the key points and extract the most critical details from these results, ensuring that the summary is both concise and accurate.

            Create a professional, standards-compliant report incorporating the following expert approaches and best practices:

            Contextual Analysis: Thoroughly analyze the background, audience, objectives, and relevant industry standards to ensure the report is well-informed and relevant.
            Clear and Concise Language: Use precise and straightforward language to enhance readability and ensure the report is easily understood.
            Logical Organization: Structure the content logically and hierarchically, following a clear and systematic approach to content presentation.
            Step-by-Step Guidance: Include step-by-step instructions or improvements as necessary to clarify complex points and facilitate understanding.
            Compliance and Standards: Adhere to all legal, ethical, and regulatory requirements, and ensure the report complies with relevant international standards and practices.
            Thorough Revision: Conduct comprehensive revisions and proofreading to eliminate errors, inconsistencies, and ensure high-quality content.
            Accessibility: Design the report to be accessible to all users, including those with disabilities, by following WCAG (Web Content Accessibility Guidelines) standards.
            User-Centric Focus: Tailor the content to address the specific needs and expectations of the target audience, ensuring it is relevant and engaging.
            
            Ensure that the final report is polished, professional, and meets the highest standards of technical writing.
            """

            if additional_params:
                for key, value in additional_params.items():
                    prompt += f"\n\nAdditional {key}: {self.sanitize_input(str(value))}"

            logger.info("Prompt generated successfully.")
            return prompt
        except Exception as e:
            logger.error(f"Error in generating prompt: {str(e)}")
            raise

    def get_ai_response(self, prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    temperature=0.2,
                    max_tokens=8192,
                )
                response_content = chat_completion.choices[0].message.content
                logger.info("AI response received successfully.")
                return response_content
            except (ValueError, TypeError) as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"Max retries reached. Error: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Unexpected error occurred while getting AI response: {str(e)}")
                logger.error(traceback.format_exc())
                raise

    def check_grammar(self, text: str) -> str:
        """Check the grammar of the provided text using LanguageTool API."""
        url = "https://api.languagetool.org/v2/check"
        data = {
            'text': text,
            'language': 'en-US'
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()

            if 'matches' in result:
                corrected_text = text
                for match in result['matches']:
                    if 'replacements' in match and match['replacements']:
                        replacement = match['replacements'][0]['value']
                        offset = match['offset']
                        length = match['length']
                        corrected_text = (corrected_text[:offset] + replacement + corrected_text[offset + length:])
                return corrected_text
            return text
        except requests.RequestException as e:
            logger.error(f"Grammar check request failed: {str(e)}")
            return text

    def process_request(self, content: str, approach: str, purpose: str, category: str, 
                        additional_params: Optional[Dict[str, Any]] = None) -> str:
        try:
            prompt = self.generate_prompt(content, approach, purpose, category, additional_params)
            response = self.get_ai_response(prompt)
            checked_response = self.check_grammar(response)
            return checked_response
        except Exception as e:
            logger.error(f"Error in processing request: {str(e)}")
            raise
