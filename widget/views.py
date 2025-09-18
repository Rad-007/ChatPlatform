from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_GET
from django.utils.html import escape
from chatbots.models import Bot


@require_GET
def embed_js(request, token: str):
    try:
        bot = Bot.objects.get(token=token, is_active=True)
    except Bot.DoesNotExist:
        return HttpResponseNotFound("// Bot not found")

    origin = request.build_absolute_uri("/").rstrip("/")
    primary = escape(bot.primary_color)
    position = bot.position
    js = f"""
    (function() {{
      const token = {token!r};
      const origin = {origin!r};
      if (document.getElementById('cbp-frame-' + token)) return;
      const iframe = document.createElement('iframe');
      iframe.src = origin + '/widget/b/' + token + '/';
      iframe.id = 'cbp-frame-' + token;
      iframe.style.position = 'fixed';
      iframe.style.zIndex = '2147483647';
      iframe.style.border = 'none';
      iframe.style.width = '360px';
      iframe.style.height = '520px';
      iframe.style.background = 'transparent';
      iframe.style.{ 'right' if position=='bottom-right' else 'left' } = '16px';
      iframe.style.bottom = '16px';
      document.body.appendChild(iframe);
    }})();
    """
    return HttpResponse(js, content_type="application/javascript")


@require_GET
def widget_page(request, token: str):
    bot = get_object_or_404(Bot, token=token, is_active=True)
    return render(request, "widget/widget.html", {"bot": bot})

