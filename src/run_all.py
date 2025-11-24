import os
import subprocess
import sys

# ================================
# 0. Rutas base del proyecto
# ================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(BASE_DIR, "src")

ORCHESTRATOR = os.path.join(SRC_PATH, "orchestrator.py")
ANALYSIS = os.path.join(SRC_PATH, "analysis.py")

print("🔧 Ejecutando proyecto ENDO completo")
print("📌 Carpeta base:", BASE_DIR)
print("📌 Orchestrator:", ORCHESTRATOR)
print("📌 Analysis:", ANALYSIS)
print("=" * 60)


# ================================
# 1. Ejecutar Orchestrator
# ================================
print("🚀 Ejecutando pipeline (orchestrator.py)...")

try:
    subprocess.run([sys.executable, ORCHESTRATOR], check=True)
    print("✅ Pipeline ejecutado correctamente.\n")
except subprocess.CalledProcessError as e:
    print("❌ ERROR ejecutando el pipeline.")
    print(e)
    sys.exit(1)


# ================================
# 2. Ejecutar análisis final
# ================================
print("📊 Ejecutando análisis de datos (analysis.py)...")

try:
    subprocess.run([sys.executable, ANALYSIS], check=True)
    print("✅ Análisis ejecutado correctamente.\n")
except subprocess.CalledProcessError as e:
    print("❌ ERROR ejecutando análisis.")
    print(e)
    sys.exit(1)


# ================================
# 3. Final
# ================================
print("=" * 60)
print(" TODO EL PROYECTO SE EJECUTÓ EXITOSAMENTE")
print(" Resultados en:")
print("    data/processed/")
print("    reports/figures/")
print("    reports/metrics/")
print("    pipeline_execution.log")
print("=" * 60)
