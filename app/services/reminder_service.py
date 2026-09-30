from datetime import datetime
def due_reminders(medicines, now=None):
    """Return medicines whose HH:MM schedule matches the current local minute."""
    now=now or datetime.now(); minute=now.strftime("%H:%M")
    return [m for m in medicines if minute in [t.strip() for t in (m.times or "").split(",")]]
