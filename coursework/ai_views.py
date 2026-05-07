# coursework/ai_views.py
import os
import PyPDF2
from groq import Groq
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Document

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class ChatWithPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):
        user_message = request.data.get('message')
        
        if not user_message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # FIXED: Removed 'owner=request.user' so students can read admin documents
            document = Document.objects.get(id=document_id)
            
            pdf_text = ""
            with document.file.open('rb') as f:
                reader = PyPDF2.PdfReader(f)
                # Read up to the first 10 pages to give the AI more context
                num_pages = min(len(reader.pages), 10)
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    extracted = page.extract_text()
                    if extracted:
                        pdf_text += extracted + "\n"

            # Truncate text just to be safe (roughly 6000 words limit for Groq Llama 3)
            pdf_text = pdf_text[:25000] 

            system_prompt = f"""You are a helpful AI tutor for a student. 
            Answer their questions strictly based on the following document content.
            If the answer is not in the document, say "I cannot find that in the document."
            
            DOCUMENT CONTENT:
            {pdf_text}
            """

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.3, 
                max_tokens=1024,
            )

            ai_response = chat_completion.choices[0].message.content
            return Response({"reply": ai_response}, status=status.HTTP_200_OK)

        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)