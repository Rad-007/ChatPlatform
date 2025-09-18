import json
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from chatbots.models import Bot
from .models import Conversation, Message
from .ai import generate_response, stream_response_chunks


def _get_session_id(request):
    sid = request.GET.get("session_id") or request.POST.get("session_id")
    if not sid:
        # fallback to header
        sid = request.headers.get("X-Session-ID")
    return sid


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request, token: str):
    bot = get_object_or_404(Bot, token=token, is_active=True)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")
    content = payload.get("message", "").strip()
    session_id = payload.get("session_id") or _get_session_id(request)
    if not content or not session_id:
        return HttpResponseBadRequest("message and session_id are required")

    # Find or create conversation
    conv, _ = Conversation.objects.get_or_create(bot=bot, session_id=session_id, defaults={"started_at": now()})
    Message.objects.create(conversation=conv, role="user", content=content)

    # If client requests no immediate answer (will use streaming), skip generation
    no_answer = bool(payload.get("no_answer"))
    if no_answer:
        return JsonResponse({
            "conversation_id": conv.id,
            "reply": None,
        })

    # AI response (synchronous, non-streaming)
    answer = generate_response(bot, conv)
    Message.objects.create(conversation=conv, role="assistant", content=answer)

    return JsonResponse({
        "conversation_id": conv.id,
        "reply": answer,
    })


@csrf_exempt
def stream_response(request, token: str):
    bot = get_object_or_404(Bot, token=token, is_active=True)
    session_id = _get_session_id(request)
    if not session_id:
        return HttpResponseBadRequest("session_id required")
    try:
        conv = Conversation.objects.get(bot=bot, session_id=session_id)
    except Conversation.DoesNotExist:
        return HttpResponseNotFound("Conversation not found")

    def event_stream():
        yield "retry: 1000\n\n"
        acc = ""
        for chunk in stream_response_chunks(bot, conv):
            acc += chunk
            data = json.dumps({"delta": chunk})
            yield f"data: {data}\n\n"
        # save final message after stream completes
        Message.objects.create(conversation=conv, role="assistant", content=acc)
        yield f"data: {json.dumps({'done': True})}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response


@csrf_exempt
@require_http_methods(["GET"])
def get_history(request, token: str):
    bot = get_object_or_404(Bot, token=token, is_active=True)
    session_id = _get_session_id(request)
    if not session_id:
        return HttpResponseBadRequest("session_id required")
    try:
        conv = Conversation.objects.get(bot=bot, session_id=session_id)
    except Conversation.DoesNotExist:
        return JsonResponse({"messages": []})

    msgs = conv.messages.order_by("created_at").values("role", "content", "created_at")
    return JsonResponse({"messages": list(msgs)})

