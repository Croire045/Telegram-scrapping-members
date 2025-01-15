import sys
import csv
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty


# Configuration de l'API Telegram
API_ID = 11111111  # Remplacez par votre API ID
API_HASH = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'  # Remplacez par votre API Hash
PHONE = '+1111111111111111'  # Remplacez par votre numéro de téléphone

# Réglage de l'encodage de la sortie pour éviter les erreurs Unicode
sys.stdout.reconfigure(encoding='utf-8')

# Initialise le client Telegram
with TelegramClient(PHONE, API_ID, API_HASH) as client:
    if not client.is_user_authorized():
        client.send_code_request(PHONE)
        code = input('Enter the code sent to your phone: ')
        client.sign_in(PHONE, code)

    # Récupère les groupes disponibles
    print("Fetching group list...")
    chats = []
    last_date = None
    chunk_size = 200
    groups = []

    try:
        result = client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)
    except Exception as e:
        print(f"Error fetching groups: {e}")
        exit()

    for chat in chats:
        if getattr(chat, 'megagroup', False):  # Vérifie si c'est un méga-groupe
            groups.append(chat)

    # Liste les groupes et demande à l'utilisateur de choisir
    if not groups:
        print("No groups found.")
        exit()

    print('Choose a group to scrape members from:')
    for i, group in enumerate(groups):
        print(f"{i} - {group.title}")

    while True:
        try:
            g_index = int(input("Enter a group number: "))
            if 0 <= g_index < len(groups):
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    target_group = groups[g_index]
    print(f"Selected group: {target_group.title}")

    # Récupère les membres du groupe
    print('Fetching members...')
    try:
        all_participants = client.get_participants(target_group, aggressive=True)
    except Exception as e:
        print(f"Error fetching members: {e}")
        exit()

    # Sauvegarde les membres dans un fichier CSV
    output_file = "members.csv"
    print(f"Saving members to {output_file}...")
    try:
        with open(output_file, "w", encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])
            for user in all_participants:
                username = user.username or ""
                first_name = user.first_name or ""
                last_name = user.last_name or ""
                name = (first_name + ' ' + last_name).strip()
                writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])
        print(f"Members saved successfully to {output_file}.")
    except Exception as e:
        print(f"Error saving members: {e}")
