def get_friends_list():
    return [
        {"name": "Hungry4waffles04", "flag": "🇯🇴", "status": "Offline", "last_seen": "Last seen a year ago"},
        {"name": "SirAhmed1", "flag": "🇪🇬", "status": "Online", "last_seen": "Active in Modern 26.2"},
        {"name": "SoundMax_", "flag": "🇭🇷", "status": "Offline", "last_seen": "Last seen 2 years ago"},
        {"name": "Thorfinn_Goal", "flag": "🇸🇾", "status": "Offline", "last_seen": "Last seen 2 months ago"}
    ]

def get_chat_history(friend_name):
    return [
        {"sender": friend_name, "text": "Hey! Are you jumping on the SIR 26 server today?"},
        {"sender": "me", "text": "Yeah, testing the new Bliss Shaders and 3D POM relief!"}
    ]

def send_satellite_message(friend_name, text):
    return True
