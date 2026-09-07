"""Launch restartable analysis work without a paid background-worker service."""
from threading import Thread
import httpx
from flask import Flask
from trellis.analysis_pipeline import execute_analysis_run
from trellis.extensions import db
from trellis.models import AnalysisRun
from trellis.recommendations import generate_and_persist_recommendations

def launch_analysis(app: Flask, analysis_id: int) -> None:
    def work() -> None:
        with app.app_context():
            analysis = db.session.get(AnalysisRun, analysis_id)
            if analysis is not None:
                client_factory = app.config.get("ANALYSIS_CLIENT_FACTORY")
                client = client_factory() if client_factory else httpx.Client(timeout=httpx.Timeout(20.0), follow_redirects=False)
                execute_analysis_run(
                    analysis,
                    client=client,
                    resolver=app.config.get("URL_RESOLVER") or __import__("socket").getaddrinfo,
                    pagespeed_api_key=app.config.get("PAGESPEED_API_KEY", ""),
                    recommendation_generator=lambda run: generate_and_persist_recommendations(
                        run,
                        client=client,
                        groq_api_key=app.config.get("GROQ_API_KEY", ""),
                        gemini_api_key=app.config.get("GEMINI_API_KEY", ""),
                    ),
                )
                client.close()
            db.session.remove()
    Thread(target=work, name=f"trellis-analysis-{analysis_id}", daemon=True).start()
