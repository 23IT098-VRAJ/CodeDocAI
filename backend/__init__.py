"""
CodeDocAI backend. Importing this package switches off the usage telemetry that
CrewAI (and the OpenTelemetry SDK it uses) send by default, so nothing about a scan
leaves the machine except the cloud model requests themselves. An explicit value
already in the environment is respected.
"""
import os

os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
