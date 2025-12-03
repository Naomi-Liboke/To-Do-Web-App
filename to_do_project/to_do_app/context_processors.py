def show_welcome(request):
    """Provide a one-time `show_welcome` flag from session to templates.

    This pops the session key so the welcome banner is only shown once after login.
    """
    show = False
    try:
        show = request.session.pop('show_welcome', False)
    except Exception:
        show = False
    return {'show_welcome': show}
