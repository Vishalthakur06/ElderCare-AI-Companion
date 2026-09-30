SAFE_COMMANDS={"medicines":"/medicines/","health":"/health/","appointments":"/appointments/","emergency":"/emergency/"}
def resolve_command(text):
    t=(text or "").lower()
    aliases={"medicines":["medicine","medicines","दवाई","औषध"],"health":["health","sugar","bp","सेहत","आरोग्य"],"appointments":["appointment","doctor","डॉक्टर","भेट"],"emergency":["emergency","sos","आपातकाल","मदत"]}
    for key,words in aliases.items():
        if any(w in t for w in words): return SAFE_COMMANDS[key]
    return None
