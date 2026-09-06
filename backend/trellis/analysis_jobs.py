"""Launch restartable analysis work without a paid background-worker service."""
from threading import Thread
from flask import Flask
from trellis.analysis_pipeline import execute_analysis_run
from trellis.extensions import db
from trellis.models import AnalysisRun

def launch_analysis(app: Flask, analysis_id: int) -> None:
    def work() -> None:
        with app.app_context():
            analysis = db.session.get(AnalysisRun, analysis_id)
            if analysis is not None:
                client_factory = app.config.get("ANALYSIS_CLIENT_FACTORY")
                client = client_factory() if client_factory else None
                execute_analysis_run(analysis, client=client, resolver=app.config.get("URL_RESOLVER") or __import__("socket").getaddrinfo)
                if client is not None:
                    client.close()
            db.session.remove()
    Thread(target=work, name=f"trellis-analysis-{analysis_id}", daemon=True).start()
