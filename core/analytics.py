import os
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class PerformanceAnalytics:
    """
    Captures and analyzes performance metrics for the autonomous agents.
    """
    def __init__(self, storage_path: str = "./analytics"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.metrics_file = os.path.join(storage_path, "kpi_metrics.json")
        self.dashboard_file = os.path.join(storage_path, "dashboard.md")
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {
            "sessions": [],
            "aggregates": {
                "total_posts": 0,
                "total_opportunities_found": 0,
                "total_reflections": 0,
                "success_rate": 0.0
            }
        }

    def record_session(self, session_id: str, results: Any):
        """Records a Crew execution session result."""
        session_entry = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "raw_result": str(results)
        }
        self.data["sessions"].append(session_entry)
        
        # Simple heuristic analysis of results
        res_str = str(results).lower()
        if "successfully posted" in res_str or "id:" in res_str:
            self.data["aggregates"]["total_posts"] += 1
        if "opportunity" in res_str or "contest" in res_str:
            self.data["aggregates"]["total_opportunities_found"] += 1
        if "critique" in res_str or "approval" in res_str:
            self.data["aggregates"]["total_reflections"] += 1
            
        self._save_data()
        self.update_dashboard()

    def _save_data(self):
        with open(self.metrics_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def update_dashboard(self):
        """Generates a markdown dashboard summary."""
        agg = self.data["aggregates"]
        content = f"""# OpenCLAW Performance Dashboard
Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Key Performance Indicators (KPIs)
| Metric | Value |
| --- | --- |
| Total Social Posts | {agg['total_posts']} |
| Opportunities Discovered | {agg['total_opportunities_found']} |
| Reflection Cycles | {agg['total_reflections']} |
| Active Agents | 5 |

## Recent Activity
"""
        for session in self.data["sessions"][-5:]:
            content += f"- **{session['timestamp']}**: {session['session_id']}\n"
            
        with open(self.dashboard_file, 'w') as f:
            f.write(content)
        logger.info(f"Dashboard updated at {self.dashboard_file}")

if __name__ == "__main__":
    analytics = PerformanceAnalytics()
    analytics.record_session("test_session_001", "Successfully posted to Twitter. ID: 12345")
    print("Analytics test complete.")
