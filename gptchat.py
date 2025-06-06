import json
import asyncio
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from agents import Runner
from .agents import evaluation_agent
from .models import ChatTurn, TrainingSummary

@csrf_exempt
def stream_chatgpt_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()
            school_or_trust = data.get("school_or_trust", "").strip()
            staff_involved = data.get("staff_involved", "").strip()


            # STEP 1: Get or create session ID
            session_id = request.session.get("chat_session_id")
            if not session_id:
                session_id = get_random_string(32)
                request.session["chat_session_id"] = session_id

            # STEP 2: Load previous chat turns
            chat_history = list(ChatTurn.objects.filter(session_id=session_id).order_by("timestamp").values("role", "content"))

            # STEP 3: Add new user message to the chat history
            chat_history.append({"role": "user", "content": message})

            def sync_stream():
                full_response = ""

                async def generate():
                    result = Runner.run_streamed(evaluation_agent, input=[
                        {"role": "system", "content": evaluation_agent.instructions},
                        *chat_history
                    ])
                    async for event in result.stream_events():
                        if event.type == "raw_response_event" and hasattr(event.data, "delta"):
                            yield event.data.delta

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    agen = generate()
                    while True:
                        chunk = loop.run_until_complete(agen.__anext__())
                        full_response += chunk
                        yield chunk
                except StopAsyncIteration:
                    # STEP 4: Save chat history
                    ChatTurn.objects.create(session_id=session_id, role="user", content=message)
                    ChatTurn.objects.create(session_id=session_id, role="assistant", content=full_response)

                    # ✅ STEP 5: Save final response as a training summary
                    TrainingSummary.objects.create(
                        title="Training Summary",
                        school_or_trust=school_or_trust,
                        staff_involved=staff_involved,
                        summary_text=full_response,
                    )
                finally:
                    loop.close()

            return StreamingHttpResponse(sync_stream(), content_type="text/plain")

        except Exception as e:
            return StreamingHttpResponse(f"⚠️ Error: {str(e)}", content_type="text/plain", status=500)

    return StreamingHttpResponse("Method Not Allowed", status=405)

# Optional chat page view
def chat_page(request):
    return render(request, "gptchat/chat.html")

