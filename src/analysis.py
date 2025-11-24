import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from scipy.stats import f_oneway

# 0. Construir rutas de salida
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

processed_path = os.path.join(BASE_DIR, "data", "processed", "merged_sales_social.csv")

reports_fig = os.path.join(BASE_DIR, "reports", "figures")
reports_metrics = os.path.join(BASE_DIR, "reports", "metrics")

os.makedirs(reports_fig, exist_ok=True)
os.makedirs(reports_metrics, exist_ok=True)

print(" Usando ruta:", processed_path)

# 1. Cargar dataset procesado
df = pd.read_csv(processed_path)
df["date"] = pd.to_datetime(df["date"])

print(" Dataset cargado correctamente:")
print(df.head(), "\n")

# Validación columna
if "quantity_sold" not in df.columns:
    raise ValueError("ERROR: La columna 'quantity_sold' no existe en el dataset final.")

# Mostrar nulos
nulls = df.isnull().sum()
print(" Valores nulos por columna:\n", nulls, "\n")

# 2. ESTACIONALIDAD

daily_sales = df.groupby("date")["quantity_sold"].sum()

plt.figure(figsize=(12, 5))
plt.plot(daily_sales.index, daily_sales.values)
plt.title("Tendencia diaria de ventas")
plt.xlabel("Fecha")
plt.ylabel("Cantidad vendida")
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(reports_fig, "tendencia_ventas.png"))
plt.show()

print(" Análisis de estacionalidad completado.\n")

# 
# 3. CORRELACIÓN sentimiento vs ventas
daily_sentiment = df.groupby("date")["sentiment"].mean()

merged_trend = pd.DataFrame({
    "sales": daily_sales,
    "sentiment": daily_sentiment
}).dropna()

correlation = merged_trend["sales"].corr(merged_trend["sentiment"])
print(f" Correlación sentimiento–ventas: {correlation:.4f}")

# Scatter plot correlación
plt.figure(figsize=(8, 5))
sns.regplot(x="sentiment", y="sales", data=merged_trend)
plt.title("Relación entre sentimiento de redes e ingresos diarios")
plt.xlabel("Sentimiento promedio del día")
plt.ylabel("Ventas totales del día")
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(reports_fig, "correlacion_sentimiento_ventas.png"))
plt.show()

# 4. ANOVA — Diferencias entre tipos de restaurante
groups = df.groupby("restaurant_type")["quantity_sold"].apply(list)

anova_result = f_oneway(*groups)
print("\n ANOVA — Diferencias entre tipos de restaurante")
print(anova_result)

plt.figure(figsize=(10, 5))
sns.boxplot(x=df["restaurant_type"], y=df["quantity_sold"])
plt.xticks(rotation=45)
plt.title("Distribución de ventas por tipo de restaurante")
plt.tight_layout()
plt.savefig(os.path.join(reports_fig, "anova_restaurant_type.png"))
plt.show()

# 5. ARIMA — Predicción de ventas

sales_series = daily_sales.asfreq("D").fillna(method="bfill")
sales_series = sales_series.replace([float("inf"), -float("inf")], None).dropna()

try:
    model = ARIMA(sales_series, order=(5,1,2))
    model_fit = model.fit()
except Exception as e:
    print(" Error al entrenar ARIMA:", e)
    exit()

print("\n Resumen del modelo ARIMA:")
print(model_fit.summary())

future = model_fit.forecast(steps=7)

plt.figure(figsize=(12, 5))
plt.plot(sales_series, label="Histórico")
plt.plot(future.index, future, label="Pronóstico ARIMA", linestyle="--")
plt.title("Pronóstico de ventas (7 días)")
plt.xlabel("Fecha")
plt.ylabel("Ventas")
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig(os.path.join(reports_fig, "arima_forecast.png"))
plt.show()

# 6. GUARDAR RESULTADOS NUMÉRICOS

with open(os.path.join(reports_metrics, "analysis_results.txt"), "w") as f:
    f.write("CORRELACIÓN SENTIMIENTO–VENTAS\n")
    f.write(str(correlation) + "\n\n")

    f.write("RESULTADO ANOVA\n")
    f.write(str(anova_result) + "\n\n")

    f.write("PRONÓSTICO ARIMA (7 días)\n")
    f.write(str(future) + "\n\n")

# 7. CONCLUSIONES AUTOMÁTICAS
print("\n=======================")
print(" CONCLUSIONES RÁPIDAS")
print("=======================\n")

if correlation > 0.2:
    print("→ El sentimiento positivo se asocia con mayores ventas.")
elif correlation < -0.2:
    print("→ El sentimiento negativo afecta las ventas.")
else:
    print("→ El sentimiento NO tiene relación fuerte con las ventas.")

if anova_result.pvalue < 0.05:
    print("→ Sí hay diferencias significativas entre tipos de restaurante.")
else:
    print("→ NO hay diferencias estadísticas entre tipos de restaurante.")

print("→ Pronóstico ARIMA generado para los próximos 7 días.")
print("\n✔ Análisis completo finalizado con éxito.")
