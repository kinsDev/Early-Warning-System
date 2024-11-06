import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List

class Visualizer:
    def __init__(self, config: Config):
        self.config = config

    def plot_predictions_over_time(self, dates: pd.Series,
                                   predictions: np.ndarray,
                                   uncertainties: np.ndarray,
                                   actual: np.ndarray,
                                   target: str) -> None:
        """Plot predictions with uncertainty bands over time."""
        fig = go.Figure()

        # Add actual values
        fig.add_trace(go.Scatter(
            x=dates,
            y=actual,
            name='Actual',
            mode='lines',
            line=dict(color='blue')
        ))

        # Add predictions with uncertainty bands
        fig.add_trace(go.Scatter(
            x=dates,
            y=predictions,
            name='Predicted',
            mode='lines',
            line=dict(color='red')
        ))

        # Add uncertainty bands
        fig.add_trace(go.Scatter(
            x=dates,
            y=predictions + uncertainties,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            fillcolor='rgba(255, 0, 0, 0.2)',
            fill='tonexty'
        ))

        fig.add_trace(go.Scatter(
            x=dates,
            y=predictions - uncertainties,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255, 0, 0, 0.2)',
            fill='tonexty',
            showlegend=False
        ))

        fig.update_layout(
            title=f'{target} Predictions Over Time',
            xaxis_title='Date',
            yaxis_title=target,
            hovermode='x unified'
        )

        fig.write_html(self.config.output_path / f'{target}_predictions.html')