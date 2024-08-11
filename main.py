import os
from dotenv import load_dotenv
from user_interface import UserInterface
from function import DocumentProcessor
from ai_prompt import AIPrompt
import logging
import traceback
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from docx import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TechnicalWritingAssistant:
    def __init__(self):
        self.load_environment()
        self.ui = UserInterface()
        self.processor = DocumentProcessor()
        self.ai_prompt = AIPrompt()
        self.setup_callbacks()
        self.executor = ThreadPoolExecutor(max_workers=3)  

    def load_environment(self):
        try:
            load_dotenv()
            required_vars = ['GROQ_API_KEY']  
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
        except Exception as e:
            logger.error(f"Failed to load environment variables: {str(e)}")
            raise

    def setup_callbacks(self):
        self.ui.set_generate_callback(self.generate_document)
        self.ui.set_save_callback(self.save_document)
        # self.ui.set_preview_callback(self.preview_document)

    async def run(self):
        try:
            self.ui.run()
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            logger.error(traceback.format_exc())
            await self.ui.display_message("An unexpected error occurred. Please restart the application.")

    def generate_document(self, approach, purpose, category, content):
        try:
            sanitized_content = self.ui.validate_input(content)
            if len(sanitized_content) < 50:
                self.ui.display_message("Content is too short. Please provide more detailed information.")
                return None

            # Generate the AI prompt and get a response
            prompt = self.ai_prompt.generate_prompt(sanitized_content, approach, purpose, category)
            response = self.ai_prompt.get_ai_response(prompt)

            if not response:
                self.ui.display_message("Failed to generate content. Please try again.")
                return None

            # Format the generated document
            formatted_doc = self.processor.format_document(response)
            return formatted_doc
        except Exception as e:
            logger.error(f"Error in document generation: {str(e)}")
            logger.error(traceback.format_exc())
            self.ui.display_message("Error generating document. Please check the log for details.")
            return None

    def save_document(self, doc, file_path):
        try:
            if not doc:
                self.ui.display_message("No document to save. Please generate a document first.")
                return

            # Save the document to the specified file path
            self.processor.save_document(doc, file_path)
            logger.info(f"Document saved successfully: {file_path}")
            self.ui.display_message(f"Document saved successfully to {file_path}")
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            logger.error(traceback.format_exc())
            self.ui.display_message("Error saving document. Please check the log for details.")

    async def run_in_executor(self, func, *args):
        return await asyncio.get_event_loop().run_in_executor(self.executor, func, *args)

    def cleanup(self):
        self.executor.shutdown(wait=True)
        logger.info("Cleanup completed.")

if __name__ == "__main__":
    assistant = TechnicalWritingAssistant()
    try:
        asyncio.run(assistant.run())
    except KeyboardInterrupt:
        logger.info("Application terminated by user.")
    except Exception as e:
        logger.critical(f"Critical error occurred: {str(e)}")
        logger.critical(traceback.format_exc())
    finally:
        assistant.cleanup()