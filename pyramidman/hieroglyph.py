import ipywidgets as widgets
import plotly.graph_objs as go
import numpy as np
from typing import List


def plot_timeseries_range_slider(x, y, title):
    """It plots a timeseries of the given data, and includes a slider.

    Arguments:
        x {[type]} -- [description]
        y {[type]} -- [description]
        title {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=y, name="AAPL High",
                             line_color='deepskyblue'))

    fig.update_layout(title_text='Time Series with Rangeslider',
                      xaxis_rangeslider_visible=True)

    return go.FigureWidget(fig)


def create_tabs(children: List[go.Box], tab_names: List[str]):
    """It creates a tab object with the boxes (or FigureWidgets) passed as input.

    Keyword Arguments:
        children {[type]} -- [description] (default: {List[go.Box]})
        tab_names {[type]} -- [description] (default: {List[str]})

    Returns:
        [type] -- [description]
    """
    tab = widgets.Tab()
    tab.children = children

    for i in range(len(children)):
        tab.set_title(i, tab_names[i])

    return tab


def plot_spectrogram(freqs, bins, spectrogram):
    """Plots the spectrogram using the plotly functions. 
    It takes as input the output of the get_spectrogram function.

    Arguments:
        freqs {[type]} -- [description]
        bins {[type]} -- [description]
        spectrogram {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    trace = [go.Heatmap(
        x=bins,
        y=freqs,
        z=10*np.log10(spectrogram + 0.01),
        colorscale='Jet',
    )]

    layout = go.Layout(
        title='Spectrogram with plotly',
        yaxis=dict(title='Frequency'),  # x-axis label
        xaxis=dict(title='Time'),  # y-axis label
    )

    fig = go.Figure(data=trace, layout=layout)

    return go.FigureWidget(fig)


def add_word_annotations(fig, words):
    """Created anotations in a Figure widget with the words that were found.
    """

    for element in words:
        word = element["word"]
        start_time = element["start_time "]
        duration = element["duration"]

        fig.add_annotation(
            go.layout.Annotation(
                x=start_time + duration/2,
                y=0,
                text=word)
        )

        fig.add_shape(
            # Line Horizontal
            go.layout.Shape(
                type="line",
                x0=start_time,
                y0=0,
                x1=start_time + duration,
                y1=0,
                line=dict(
                    width=4,
                ),
            )
        )
    fig.update_shapes(dict(xref='x', yref='y'))
    fig.update_annotations(dict(
            xref="x",
            yref="y",
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
))