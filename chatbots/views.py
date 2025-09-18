from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Bot
from conversations.models import Conversation, Message
from .forms import BotForm


@login_required
def dashboard(request):
    bots = Bot.objects.filter(owner=request.user).order_by("-created_at")
    bot_ids = list(bots.values_list("id", flat=True))
    total_conversations = Conversation.objects.filter(bot_id__in=bot_ids).count()
    total_messages = Message.objects.filter(conversation__bot_id__in=bot_ids).count()
    return render(request, "chatbots/dashboard.html", {
        "bots": bots,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
    })


@login_required
def bot_create(request):
    form = BotForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        # Simple plan gate: free plan limited to 1 bot
        profile = getattr(request.user, "profile", None)
        if profile and profile.plan == "free" and Bot.objects.filter(owner=request.user).count() >= 1:
            return render(request, "chatbots/bot_form.html", {"form": form, "title": "Create Bot", "error": "Free plan allows only 1 bot. Upgrade to create more."})
        bot = form.save(commit=False)
        bot.owner = request.user
        bot.save()
        return redirect("chatbots:dashboard")
    return render(request, "chatbots/bot_form.html", {"form": form, "title": "Create Bot"})


@login_required
def bot_edit(request, pk):
    bot = get_object_or_404(Bot, pk=pk)
    if bot.owner != request.user:
        return HttpResponseForbidden()
    form = BotForm(request.POST or None, instance=bot)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("chatbots:dashboard")
    return render(request, "chatbots/bot_form.html", {"form": form, "title": "Edit Bot"})


@login_required
def bot_delete(request, pk):
    bot = get_object_or_404(Bot, pk=pk)
    if bot.owner != request.user:
        return HttpResponseForbidden()
    if request.method == "POST":
        bot.delete()
        return redirect("chatbots:dashboard")
    return render(request, "chatbots/bot_delete.html", {"bot": bot})


@login_required
def bot_embed(request, pk):
    bot = get_object_or_404(Bot, pk=pk, owner=request.user)
    # Provide snippet for embedding
    snippet = f"<script src='{request.build_absolute_uri('/widget/embed/'+bot.token+'.js')}' defer></script>"
    # Per-bot analytics
    conv_qs = Conversation.objects.filter(bot=bot).order_by("-started_at")
    msg_count = Message.objects.filter(conversation__bot=bot).count()
    recent_convs = conv_qs[:5]
    ctx = {
        "bot": bot,
        "snippet": snippet,
        "conversation_count": conv_qs.count(),
        "message_count": msg_count,
        "recent_conversations": recent_convs,
    }
    return render(request, "chatbots/bot_embed.html", ctx)

