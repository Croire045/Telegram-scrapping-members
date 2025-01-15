from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest
import csv
import time
import sys

# Configuration de l'API Telegram
API_ID = 11111111  # Remplacez par votre API ID
API_HASH = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'  # Remplacez par votre API Hash
PHONE = '+1111111111111111'  # Remplacez par votre numéro de téléphone

# Réglage de l'encodage de la sortie pour éviter les erreurs Unicode
sys.stdout.reconfigure(encoding='utf-8')

# Lien du groupe cible (directement intégré)
group_link = "https://t.me/Online4051" # remplacez par le lien que vous souhaitez booster

# Initialisation du client Telegram
with TelegramClient(PHONE, API_ID, API_HASH) as client:
    if not client.is_user_authorized():
        client.send_code_request(PHONE)
        code = input("Enter the code sent to your phone: ")
        client.sign_in(PHONE, code)

    # Récupérer le groupe cible via le lien d'invitation
    try:
        target_group = client.get_entity(group_link)
    except Exception as e:
        print(f"Error fetching group: {e}")
        exit()

    # Charger les membres depuis le fichier CSV
    input_file = "members.csv"
    print(f"Loading members from {input_file}...")
    users = []

    try:
        with open(input_file, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user = {
                    'username': row['username'],
                    'user_id': int(row['user id']),
                    'access_hash': int(row['access hash'])
                }
                users.append(user)
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        exit()
    except KeyError:
        print("Error: Missing required columns in the CSV file (username, user id, access hash).")
        exit()

    print(f"Loaded {len(users)} members from {input_file}.")

    # Ajouter les utilisateurs par session de 9
    session_size = 9  # Nombre de membres par session, limitez vous par ce nombre car au-délà de ce nombre vous risquerez d'etre bani de telegram
    total_members = len(users)
    count = 0

    print("Adding members to the group...")

    for i in range(0, total_members, session_size):
        # Limiter à 9 membres par session
        session_users = users[i:i + session_size]
        print(f"Processing members {i + 1} to {min(i + session_size, total_members)}...")

        for user in session_users:
            try:
                if user['username']:
                    user_entity = client.get_entity(user['username'])
                else:
                    user_entity = InputPeerUser(user['user_id'], user['access_hash'])

                client(InviteToChannelRequest(  # Utilisation correcte après import
                    channel=target_group,
                    users=[user_entity]
                ))
                print(f"Added {user['username'] or user['user_id']} successfully.")
                count += 1
                time.sleep(1)  # Pause de 3 secondes entre chaque ajout

            except PeerFloodError:
                print("Error: Reached Telegram's limit. Try again later.")
                break
            except UserPrivacyRestrictedError:
                print(f"Error: {user['username'] or user['user_id']} has privacy settings that prevent adding.")
            except Exception as e:
                print(f"Error adding {user['username'] or user['user_id']}: {e}")
            time.sleep(1)  # Pause supplémentaire entre les invitations

        print(f"Finished adding {min(i + session_size, total_members)} members.")

    print(f"Successfully added {count} members to the group.")