import asyncio
import json
import httpx
from celery import shared_task
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.document import Document, DocumentStatusEnum
from sqlalchemy import select

def extract_invoice_data_sync(document_id: str):
    asyncio.run(extract_invoice_data_async(document_id))

async def extract_invoice_data_async(document_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Document).where(Document.id == document_id))
        document = result.scalar_one_or_none()
        if not document:
            return
        
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(document.file_url)
                file_bytes = response.content
                
                # Guess mime type based on url
                mime_type = 'application/pdf'
                if document.file_url.lower().endswith('.png'):
                    mime_type = 'image/png'
                elif document.file_url.lower().endswith(('.jpg', '.jpeg')):
                    mime_type = 'image/jpeg'
                
            prompt = """
            Extract the following information from this invoice or credit note:
            - Vendor Name
            - Invoice Number
            - Invoice Date (YYYY-MM-DD format)
            - VAT Amount (number only)
            - Subtotal (number only)
            - Total Amount (number only)
            - Currency (3-letter code)
            - Document Type (invoice or credit_note)
            - Confidence Score (A number between 0.0 and 1.0 representing your confidence in the extracted data)
            
            Return the result as a valid JSON object. Do not include markdown formatting like ```json.
            If a field is missing, set its value to null.
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                    prompt
                ]
            )
            
            extracted_text = response.text.strip()
            if extracted_text.startswith("```json"):
                extracted_text = extracted_text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(extracted_text)
            
            document.vendor_name = data.get("Vendor Name")
            document.invoice_number = data.get("Invoice Number")
            
            from datetime import datetime
            date_str = data.get("Invoice Date")
            if date_str:
                try:
                    document.invoice_date = datetime.strptime(date_str.strip()[:10], "%Y-%m-%d")
                except Exception as date_err:
                    print(f"Failed to parse date string {date_str}: {date_err}")
                    document.invoice_date = None
            else:
                document.invoice_date = None

            
            def parse_num(val):
                if val is None: return None
                try: return float(str(val).replace(',', ''))
                except: return None
                
            document.vat_amount = parse_num(data.get("VAT Amount"))
            document.subtotal_amount = parse_num(data.get("Subtotal"))
            document.total_amount = parse_num(data.get("Total Amount"))
            document.currency = data.get("Currency")
            document.document_type = data.get("Document Type")
            document.confidence_score = parse_num(data.get("Confidence Score"))
            document.status = DocumentStatusEnum.pending_review
            
            await db.commit()
            
            # Trigger duplicate check
            from app.tasks.duplicate import check_duplicates_async
            await check_duplicates_async(str(document.id))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Extraction failed: {e}")
            document.status = DocumentStatusEnum.rejected
            await db.commit()


@shared_task(name="app.tasks.extraction.process_document")
def process_document(document_id: str):
    extract_invoice_data_sync(document_id)
