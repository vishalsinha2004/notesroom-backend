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
            document = Document.objects.get(id=document_id)
            
            pdf_text = ""
            with document.file.open('rb') as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = min(len(reader.pages), 10)
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    extracted = page.extract_text()
                    if extracted:
                        pdf_text += extracted + "\n"

            pdf_text = pdf_text[:25000] 

            # UPDATED: High-power prompt for structured, diagram-rich, and accurate PDF extraction
            system_prompt = f"""You are a brilliant, highly analytical, and engaging AI tutor. Your primary goal is to provide immensely powerful and clear answers based strictly on the provided document.

            CRITICAL INSTRUCTIONS:
            1. ACCURACY FIRST: Answer purely based on the DOCUMENT CONTENT below. If the answer isn't there, firmly but politely state: "I cannot find that in the document."
            2. POWERFUL FLOW: Structure your response perfectly. Start with a direct answer -> Detailed explanation -> Real-world/practical examples (derived from the text) -> Empowering summary.
            3. ATTRACTIVE FORMATTING: Use rich Markdown heavily. Use headers (###), bold text for keywords, and bullet points to break down complex ideas.
            4. DIAGRAMS & VISUALS: Whenever explaining a process, relationship, or architecture found in the document, you MUST include a Mermaid.js flowchart (enclosed in ```mermaid ... ```).
            5. STRICT MERMAID RULES: You MUST use exact, valid Mermaid syntax. Use `-->` for solid links. Use `-.->` for dotted links. NEVER use invalid arrows like `|>`, `->`, or `=>`. Do not use special characters in node definitions unless wrapped in quotes.
            6. EXAMPLES: Always pull or extrapolate at least one clear, concrete example based on the text to ensure the user fully understands the concept.

            DOCUMENT CONTENT:
            {pdf_text}
            """

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.3, # Keep this low to maintain high accuracy with the PDF context
                max_tokens=2048, # Increased to allow room for diagrams and examples
            )

            ai_response = chat_completion.choices[0].message.content
            return Response({"reply": ai_response}, status=status.HTTP_200_OK)

        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GeneralChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message')
        
        if not user_message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # UPDATED: High-power prompt for empathetic, beautifully structured general chat
            system_prompt = """You are a highly empathetic, brilliant, and powerful AI tutor for students using the Notesroom application. 
            
            CRITICAL INSTRUCTIONS FOR EVERY RESPONSE:
            1. EMOTIONAL INTELLIGENCE: Analyze the user's emotional tone and match it using highly relevant emojis:
               - Powerful/Ambitious: 🚀, 💪, 🔥, 🌟, ⚡
               - Confused/Stressed: 💙, 🥺, 🫂, 🌱, 💡
               - Happy/Excited: 🎉, ✨, 😊, 🤩
            2. ATTRACTIVE FORMATTING: Your answers must be visually stunning. Use beautiful Markdown styling (headers, bolding, italics, blockquotes, and ordered/unordered lists). Do not output raw HTML.
            3. PROPER FLOW: Use the following structure for educational queries:
               - Hook/Greeting (match the emotion)
               - Core Explanation (clear, concise, accurate)
               - Detailed Examples (always provide 1-2 real-world, concrete examples to cement the idea)
               - Visual/Diagram (see below)
               - Conclusion/Next Steps (motivational wrap-up)
            4. DIAGRAMS: If the question involves a system, workflow, cycle, step-by-step process, or relationships, YOU MUST generate a Mermaid.js diagram (enclosed in ```mermaid ... ``` code blocks).
            5. STRICT MERMAID SYNTAX: You MUST use perfectly valid Mermaid.js syntax. Always start with `flowchart TD` or `flowchart LR`. Use ONLY `-->` for solid arrows and `-.->` for dotted arrows. NEVER use `|>`, `=>`, or `->`. Keep node labels simple.
            6. EXAMPLES ARE MANDATORY: Never explain a theory without grounding it in a practical, easy-to-understand example.

            Be powerful, inspiring, and incredibly helpful!"""
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                # 🔥 UPGRADED TO THE 70B MODEL 🔥
                model="llama-3.3-70b-versatile",
                temperature=0.7, 
                max_tokens=2048,
            )

            ai_response = chat_completion.choices[0].message.content
            return Response({"reply": ai_response}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)