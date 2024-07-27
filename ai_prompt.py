import os
import logging
import traceback
from groq import Groq
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIPrompt:
    def __init__(self):
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set.")
            self.client = Groq(api_key=api_key)
            logger.info("Groq client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            raise

    def sanitize_input(self, text: str, max_length: int = 3000) -> str:
        """Sanitize and truncate input text."""
        return ' '.join(text.strip().split())[:max_length]

    def generate_prompt(self, content: str, approach: str, purpose: str, category: str, 
                        additional_params: Optional[Dict[str, Any]] = None) -> str:
        try:
            sanitized_content = self.sanitize_input(content)
            sanitized_approach = self.sanitize_input(approach)
            sanitized_purpose = self.sanitize_input(purpose)
            sanitized_category = self.sanitize_input(category)
            
            prompt = f"""
            As a senior technical writer and content creator, generate a professional, standards-compliant report based on the following parameters:

            Content: {sanitized_content}
            Approach: {sanitized_approach}
            Purpose: {sanitized_purpose}
            Category: {sanitized_category}

            Adhere to relevant international standards including but not limited to:
            - ISO/IEC 26514 for systems and software engineering documentation
            - ISO/IEC/IEEE 15288 for systems engineering processes
            - DITA (Darwin Information Typing Architecture) for technical content
            - ISO 9001:2015 for quality management systems documentation
            - IEEE 1063 for software user documentation
            - ISO/IEC 25062 for usability reports
            - The Chicago Manual of Style for editorial practice

            Apply these expert approaches and best practices:
            1. Contextual Analysis: Thoroughly understand the background, audience, and objectives.
            2. Clear and Concise Language: Use precise language to ensure clarity.
            3. Structured Content: Organize information logically and hierarchically.
            4. Visual Aids: Integrate charts, diagrams, and tables where applicable.
            5. Revision and Proofreading: Ensure the document is free of errors and inconsistencies.
            6. Accessibility: Make the content accessible to all users, including those with disabilities.

            Create a comprehensive and well-structured report with complete details tailored for a Senior Technical Writer.

            Include the following content based on the category:
            - Medical Reports: Patient data privacy considerations and regulatory compliance (e.g., HIPAA).
            - Business Reports: Financial analysis, market research, and strategic recommendations.
            - Technical Reports: Detailed methodologies, technical specifications, and performance data.
            - Environmental Reports: Impact assessments, sustainability considerations, and regulatory compliance.

            Formatting Guidelines:
            - Use clear, professional language appropriate for the target audience
            - Maintain consistent terminology throughout the document
            - Use active voice and present tense where appropriate
            - Define all acronyms at first use
            - Suggest appropriate places for visualizations (charts, diagrams, etc.)

            Focus on accuracy, clarity, and professionalism in the content.
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

    def process_request(self, content: str, approach: str, purpose: str, category: str, 
                        additional_params: Optional[Dict[str, Any]] = None) -> str:
        try:
            prompt = self.generate_prompt(content, approach, purpose, category, additional_params)
            response = self.get_ai_response(prompt)
            return response
        except Exception as e:
            logger.error(f"Error in processing request: {str(e)}")
            raise
