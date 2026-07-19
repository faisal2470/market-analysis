import plotly.graph_objects as go


def plot_candlestick(df, *, title: str = "Candlestick Chart", show_volume: bool = False, width: int = 1200, height: int = 700):
    """
    Plot an interactive candlestick chart.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame indexed by date/datetime with columns:
        Open, High, Low, Close.
        Optionally Volume.
    title : str, optional
        Figure title.
    show_volume : bool, optional
        Display trading volume.
    width : int
        Figure width in pixels.
    height : int
        Figure height in pixels.
    """

    fig = go.Figure()

    # ----------------------------------------------------
    # Candlesticks
    # ----------------------------------------------------

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
            increasing_line_color="#26A69A",
            decreasing_line_color="#EF5350",
            increasing_fillcolor="#26A69A",
            decreasing_fillcolor="#EF5350",
        )
    )

    # ----------------------------------------------------
    # Volume
    # ----------------------------------------------------

    if show_volume and "Volume" in df.columns:

        colors = [
            "#26A69A" if c >= o else "#EF5350"
            for o, c in zip(df["Open"], df["Close"])
        ]

        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df["Volume"],
                marker_color=colors,
                opacity=0.30,
                name="Volume",
                yaxis="y2",
            )
        )

        fig.update_layout(
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False,
            )
        )

    # ----------------------------------------------------
    # Layout
    # ----------------------------------------------------

    fig.update_layout(
        title=title,
        template="plotly_white",
        width=width,
        height=height,

        hovermode="x unified",

        xaxis_title="Date",
        yaxis_title="Price",

        xaxis_rangeslider_visible=False,

        dragmode="zoom",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),

        margin=dict(
            l=60,
            r=40,
            t=60,
            b=40,
        ),
    )

    # ----------------------------------------------------
    # Make trading days equally spaced
    # ----------------------------------------------------

    fig.update_xaxes(
        type="category",
        showgrid=True,
        rangeslider_visible=False,
    )

    # ----------------------------------------------------
    # Grid
    # ----------------------------------------------------

    fig.update_yaxes(
        showgrid=True,
        gridcolor="lightgray",
        zeroline=False,
    )

    fig.show()


    
