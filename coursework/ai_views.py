# coursework/ai_views.py
import os
import PyPDF2
from groq import Groq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Document

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class ChatWithPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):
        user_message = request.data.get('message')
        
        if not user_message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Ensure the user owns this document
            document = Document.objects.get(id=document_id, owner=request.user)
            
            # 2. Extract text from the PDF
            pdf_text = ""
            with document.file.open('rb') as f:
                reader = PyPDF2.PdfReader(f)
                # Read up to the first 5 pages to avoid token limits on huge PDFs
                num_pages = min(len(reader.pages), 5)
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    pdf_text += page.extract_text() + "\n"

            # Truncate text just to be safe (roughly 6000 words limit for context)
            pdf_text = pdf_text[:25000] 

            # 3. Create the prompt for Llama 3
            system_prompt = f"""You are a helpful AI tutor for a student. 
            Answer their questions strictly based on the following document content.
            If the answer is not in the document, say "I cannot find that in the document."
            
            DOCUMENT CONTENT:
            {pdf_text}
            """

            # 4. Call Groq API
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.3, # Keep it focused and analytical
                max_tokens=1024,
            )

            ai_response = chat_completion.choices[0].message.content

            return Response({"reply": ai_response}, status=status.HTTP_200_OK)

        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)