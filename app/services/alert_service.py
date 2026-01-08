from app.config.settings import settings

class AlertService:
    """
    Por ahora: imprime a consola.
    Luego puedes: Telegram, Discord, Webhook, Email, etc.
    """

    async def send_entry_alert(self, payload: dict) -> None:
        if settings.ALERT_MODE == "console":
            print("\n=== ALERTA ENTRADA ===")
            for k, v in payload.items():
                print(f"{k}: {v}")

    async def send_close_alert(self, payload: dict) -> None:
        if settings.ALERT_MODE == "console":
            print("\n=== ALERTA CIERRE (WIN/LOSS) ===")
            for k, v in payload.items():
                print(f"{k}: {v}")
