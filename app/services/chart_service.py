import plotly.graph_objects as go
import pandas as pd

class ChartService:
    """
    Devuelve HTML embebible (TradingView no se integra directo con Python),
    pero acá puedes visualizar el gráfico en tu propio endpoint.
    """

    def render_trade_chart_html(self, df: pd.DataFrame, trade: dict) -> str:
        fig = go.Figure(data=[
            go.Candlestick(
                x=df["open_time"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price"
            )
        ])

        entry = trade["entry_price"]
        sl = trade["stop_loss"]
        tp = trade["take_profit"]

        # Líneas horizontales
        fig.add_hline(y=entry, line_dash="dash", annotation_text="ENTRY")
        fig.add_hline(y=sl, line_dash="dot", annotation_text="SL")
        fig.add_hline(y=tp, line_dash="dot", annotation_text="TP")

        fig.update_layout(
            title=f'{trade["symbol"]} {trade["timeframe"]} | Trade #{trade["id"]}',
            xaxis_title="Time",
            yaxis_title="Price",
            height=650,
        )

        return fig.to_html(full_html=False, include_plotlyjs="cdn")
