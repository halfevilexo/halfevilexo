import json
import asyncio
import logging
from datetime import datetime, timedelta
from telethon import TelegramClient, errors

# API ID und API Hash aus den von dir bereitgestellten Daten
api_id = 29911558
api_hash = '7d20b66641580faf28d5c5ac0a1dc1f5'

# Erstellen eines Telegram-Clients
client = TelegramClient('session_name', api_id, api_hash)

# Pfad zur JSON-Datei, die die Nachricht enthält
json_file_path = 'message.json'

# Einrichten der Protokollierung
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funktion zum Laden der Nachricht aus der JSON-Datei
def load_message():
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        return data['message']

# Hauptfunktion des Bots
async def main():
    # Verbinde den Client
    await client.start(phone=lambda: input("Bitte geben Sie Ihre Telefonnummer ein: "))
    logger.info('Bot gestartet und verbunden.')

    # Initiale Gruppen- und Benutzerliste abrufen und anzeigen
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            logger.info(f'Gruppe gefunden: {dialog.name} (ID: {dialog.id})')
        elif dialog.is_user:
            logger.info(f'Benutzer gefunden: {dialog.name} (ID: {dialog.id})')

    # Wiederhole die Aufgabe jede Stunde
    while True:
        message = load_message()
        logger.info(f'Nachricht geladen: {message}')

        # Nachrichten an Gruppen senden
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                try:
                    await client.send_message(dialog.id, message)
                    logger.info(f'Nachricht gesendet an Gruppe: {dialog.name} (ID: {dialog.id})')
                except errors.ChatWriteForbiddenError:
                    logger.warning(f'Keine Schreibberechtigung in der Gruppe: {dialog.name} (ID: {dialog.id})')
                except errors.BadRequestError as e:
                    if 'TOPIC_CLOSED' in str(e):
                        logger.warning(f'Thema geschlossen in Gruppe: {dialog.name} (ID: {dialog.id})')
                    else:
                        logger.error(f'Unerwarteter Fehler in Gruppe: {dialog.name} (ID: {dialog.id}): {e}')
                await asyncio.sleep(5)  # 5 Sekunden Pause nach dem Senden der Nachricht

        # Nachrichten an Benutzer senden
        async for dialog in client.iter_dialogs():
            if dialog.is_user:
                try:
                    await client.send_message(dialog.id, message)
                    logger.info(f'Nachricht gesendet an Benutzer: {dialog.name} (ID: {dialog.id})')
                except errors.ChatWriteForbiddenError:
                    logger.warning(f'Keine Schreibberechtigung für den Benutzer: {dialog.name} (ID: {dialog.id})')
                except errors.BadRequestError as e:
                    if 'TOPIC_CLOSED' in str(e):
                        logger.warning(f'Thema geschlossen für Benutzer: {dialog.name} (ID: {dialog.id})')
                    else:
                        logger.error(f'Unerwarteter Fehler für Benutzer: {dialog.name} (ID: {dialog.id}): {e}')
                await asyncio.sleep(5)  # 5 Sekunden Pause nach dem Senden der Nachricht

        # Warte eine Stunde bis zur nächsten Nachricht
        logger.info(f'Warten auf die nächste Nachricht um {datetime.now() + timedelta(hours=1)}')
        await asyncio.sleep(3600)

# Ausführen des Bots
with client:
    client.loop.run_until_complete(main())
