import json
import asyncio
import logging
from datetime import datetime, timedelta
from telethon import TelegramClient, errors

# API ID und API Hash aus den von dir bereitgestellten Daten
#api_id = 29911558
#api_hash = '7d20b66641580faf28d5c5ac0a1dc1f5'

api_id = 25850901
api_hash = 'ebcb63b69bf5a19fff1449773342bcd7'

# Erstellen eines Telegram-Clients
client = TelegramClient('session_name', api_id, api_hash)

# Pfad zur JSON-Datei, die die Nachricht enthält
message_json_file_path = 'message.json'
# Pfad zur JSON-Datei, die die Gruppen-, Kanal- und Benutzerliste enthält
groups_channels_users_json_file_path = 'groups_channels_users.json'

# Einrichten der Protokollierung
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funktion zum Laden der Nachricht aus der JSON-Datei
def load_message():
    with open(message_json_file_path, 'r') as file:
        data = json.load(file)
        return data['message']

# Funktion zum Laden der Gruppen-, Kanal- und Benutzerliste aus der JSON-Datei
def load_groups_channels_users():
    try:
        with open(groups_channels_users_json_file_path, 'r') as file:
            data = json.load(file)
            return data['groups'], data['channels'], data['users']
    except FileNotFoundError:
        return [], [], []

# Funktion zum Speichern der Gruppen-, Kanal- und Benutzerliste in der JSON-Datei
def save_groups_channels_users(groups, channels, users):
    with open(groups_channels_users_json_file_path, 'w') as file:
        json.dump({"groups": groups, "channels": channels, "users": users}, file, indent=4)

# Hauptfunktion des Bots
async def main():
    # Verbinde den Client
    await client.start(phone=lambda: input("Bitte geben Sie Ihre Telefonnummer ein: "))
    logger.info('Bot gestartet und verbunden.')

    # Lade existierende Gruppen-, Kanal- und Benutzerliste
    groups, channels, users = load_groups_channels_users()

    # Initiale Gruppen-, Kanal- und Benutzerliste abrufen und anzeigen
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            if dialog.id not in groups:
                logger.info(f'Neue Gruppe gefunden: {dialog.name} (ID: {dialog.id})')
                groups.append(dialog.id)
            else:
                logger.info(f'Gruppe bereits in der Liste: {dialog.name} (ID: {dialog.id})')

        elif dialog.is_channel:
            if dialog.id not in channels:
                logger.info(f'Neuer Kanal gefunden: {dialog.name} (ID: {dialog.id})')
                channels.append(dialog.id)
            else:
                logger.info(f'Kanal bereits in der Liste: {dialog.name} (ID: {dialog.id})')

        elif dialog.is_user:
            if dialog.id not in users:
                logger.info(f'Neuer Benutzer gefunden: {dialog.name} (ID: {dialog.id})')
                users.append(dialog.id)
            else:
                logger.info(f'Benutzer bereits in der Liste: {dialog.name} (ID: {dialog.id})')

    # Speichere aktualisierte Gruppen-, Kanal- und Benutzerliste
    save_groups_channels_users(groups, channels, users)

    # Wiederhole die Aufgabe jede Stunde
    while True:
        message = load_message()
        logger.info(f'Nachricht geladen: {message}')

        # Nachrichten an Gruppen senden
        for group in groups:
            try:
                await client.send_message(group, message)
                logger.info(f'Nachricht gesendet an Gruppe: {group}')
                await asyncio.sleep(5)  # Warte 5 Sekunden bevor die nächste Nachricht gesendet wird
            except errors.ChatWriteForbiddenError:
                logger.warning(f'Keine Schreibberechtigung in der Gruppe: {group}')
                groups.remove(group)
                save_groups_channels_users(groups, channels, users)
            except errors.BadRequestError as e:
                if 'TOPIC_CLOSED' in str(e):
                    logger.warning(f'Thema geschlossen in Gruppe: {group}')
                else:
                    logger.error(f'Fehler beim Senden der Nachricht an Gruppe: {group} - {e}')
                groups.remove(group)
                save_groups_channels_users(groups, channels, users)
            except ValueError as e:
                logger.error(f'Fehler beim Verarbeiten der Gruppe: {group} - {e}')
                groups.remove(group)
                save_groups_channels_users(groups, channels, users)

        # Nachrichten an Kanäle senden
        for channel in channels:
            try:
                await client.send_message(channel, message)
                logger.info(f'Nachricht gesendet an Kanal: {channel}')
                await asyncio.sleep(5)  # Warte 5 Sekunden bevor die nächste Nachricht gesendet wird
            except errors.ChatWriteForbiddenError:
                logger.warning(f'Keine Schreibberechtigung im Kanal: {channel}')
                channels.remove(channel)
                save_groups_channels_users(groups, channels, users)
            except errors.BadRequestError as e:
                if 'TOPIC_CLOSED' in str(e):
                    logger.warning(f'Thema geschlossen im Kanal: {channel}')
                else:
                    logger.error(f'Fehler beim Senden der Nachricht an Kanal: {channel} - {e}')
                channels.remove(channel)
                save_groups_channels_users(groups, channels, users)
            except ValueError as e:
                logger.error(f'Fehler beim Verarbeiten des Kanals: {channel} - {e}')
                channels.remove(channel)
                save_groups_channels_users(groups, channels, users)

        # Nachrichten an Benutzer senden
        for user in users:
            try:
                await client.send_message(user, message)
                logger.info(f'Nachricht gesendet an Benutzer: {user}')
                await asyncio.sleep(5)  # Warte 5 Sekunden bevor die nächste Nachricht gesendet wird
            except errors.ChatWriteForbiddenError:
                logger.warning(f'Keine Schreibberechtigung für Benutzer: {user}')
                users.remove(user)
                save_groups_channels_users(groups, channels, users)
            except errors.BadRequestError as e:
                logger.error(f'Fehler beim Senden der Nachricht an Benutzer: {user} - {e}')
                users.remove(user)
                save_groups_channels_users(groups, channels, users)
            except ValueError as e:
                logger.error(f'Fehler beim Verarbeiten des Benutzers: {user} - {e}')
                users.remove(user)
                save_groups_channels_users(groups, channels, users)

        # Warte eine Stunde bis zur nächsten Nachricht
        logger.info(f'Warten auf die nächste Nachricht um {datetime.now() + timedelta(hours=1)}')
        await asyncio.sleep(3600)

# Ausführen des Bots
with client:
    client.loop.run_until_complete(main())
