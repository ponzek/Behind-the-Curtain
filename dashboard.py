"""Behind the Curtain: Data, Defense & Dollars
Interactive Plotly Dash dashboard comparing Palantir (PLTR), Lockheed Martin (LMT) and RTX.
Developed for CPS*5745 by Karina Ponze.
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from plotly.subplots import make_subplots

from update_data import TICKERS, fetch_ticker

DATA_FILE = Path(__file__).parent / "data" / "prices.csv"
CACHE_SECONDS = 6 * 3600
NAMES = {"PLTR": "Palantir", "LMT": "Lockheed Martin", "RTX": "RTX"}
COLORS = {"PLTR": "#b388ff", "LMT": "#4dd0e1", "RTX": "#ffb74d"}
BG, PANEL, TEXT, MUTED, GRID = "#0b0d17", "#141829", "#e8eaf6", "#8c93b8", "rgba(140,147,184,0.15)"

_cache = {"ts": 0.0, "df": None, "source": ""}


def load_data():
    """Latest data from Yahoo Finance (cached); falls back to bundled snapshot."""
    if _cache["df"] is not None and time.time() - _cache["ts"] < CACHE_SECONDS:
        return _cache["df"], _cache["source"]
    try:
        df = pd.concat([fetch_ticker(t) for t in TICKERS])
        source = "Yahoo Finance (live)"
    except Exception:
        df = pd.read_csv(DATA_FILE)
        source = "Yahoo Finance (bundled snapshot)"
    df["Date"] = pd.to_datetime(df["Date"])
    _cache.update(ts=time.time(), df=df, source=source)
    return df, source


def style(fig, title, ytitle=None, xtitle=None, height=380):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=TEXT), x=0.02),
        paper_bgcolor=PANEL, plot_bgcolor=PANEL, font=dict(color=TEXT, family="Inter, Arial"),
        height=height, margin=dict(l=55, r=20, t=60, b=45),
        legend=dict(orientation="h", y=-0.2, font=dict(color=MUTED)),
        hovermode="x unified" if xtitle is None else "closest",
    )
    fig.update_xaxes(gridcolor=GRID, title=xtitle, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, title=ytitle, zeroline=False)
    return fig


def empty_fig(msg):
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(color=MUTED, size=14))
    return style(fig, "")


app = Dash(__name__, title="Behind the Curtain: Data, Defense & Dollars")
app.index_string = """<!DOCTYPE html><html><head>{%metas%}<title>{%title%}</title>
<meta name="description" content="Interactive comparison of Palantir, Lockheed Martin and RTX stock performance.">
{%favicon%}{%css%}
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
body{margin:0;background:radial-gradient(circle at 20% 0%,#1a1440 0%,#0b0d17 45%);color:#e8eaf6;font-family:Inter,Arial,sans-serif;min-height:100vh}
.wrap{max-width:1300px;margin:auto;padding:24px}
h1{font-size:2.3rem;font-weight:800;margin:0;background:linear-gradient(90deg,#b388ff,#4dd0e1,#ffb74d);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{color:#8c93b8;margin:6px 0 18px}
.card{background:#141829;border:1px solid rgba(179,136,255,.18);border-radius:14px;box-shadow:0 8px 30px rgba(0,0,0,.4);overflow:hidden}
.filters{display:flex;gap:28px;flex-wrap:wrap;padding:16px 20px;margin-bottom:18px;align-items:center}
.filters label{display:block;font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;color:#8c93b8;margin-bottom:6px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-bottom:18px}
.kpi{padding:14px 18px;border-left:4px solid}
.kpi b{font-size:1.1rem}.kpi div{color:#8c93b8;font-size:.85rem;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:18px;margin-bottom:18px}
.insight{padding:18px 24px;line-height:1.6}.insight h3{margin-top:0;color:#b388ff}
.insight li{margin-bottom:6px}
footer{text-align:center;color:#8c93b8;padding:20px;font-size:.9rem}
.DateInput_input{background:#0b0d17!important;color:#e8eaf6!important;font-family:Inter!important}
.DateRangePickerInput,.DateRangePickerInput_arrow,.DateInput{background:#0b0d17!important}
.DateRangePickerInput{border:1px solid #2a3050!important;border-radius:8px}
.cl label{display:inline-block!important;margin-right:18px;font-size:1rem!important;color:#e8eaf6!important;text-transform:none!important;letter-spacing:0!important}
@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style></head><body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body></html>"""

_df0, _ = load_data()
MIN_D, MAX_D = _df0["Date"].min().date(), _df0["Date"].max().date()
DEFAULT_START = max(MIN_D, (_df0["Date"].max() - pd.DateOffset(years=2)).date())


def graph(i):
    return html.Div(dcc.Graph(id=i, config={"displaylogo": False}), className="card")


app.layout = html.Div(className="wrap", children=[
    html.Header([
        html.H1("🕶️ Behind the Curtain: Data, Defense & Dollars"),
        html.P("Palantir (PLTR) vs. Lockheed Martin (LMT) vs. RTX — a software company against two defense "
               "manufacturers. By Karina Ponze  •  Developed for CPS*5745", className="sub"),
    ]),
    html.Div(className="card filters", children=[
        html.Div([html.Label("Companies"),
                  dcc.Checklist(id="companies", className="cl", value=TICKERS,
                                options=[{"label": f"{NAMES[t]} ({t})", "value": t} for t in TICKERS])]),
        html.Div([html.Label("Date range"),
                  dcc.DatePickerRange(id="dates", min_date_allowed=MIN_D, max_date_allowed=MAX_D,
                                      start_date=DEFAULT_START, end_date=MAX_D, display_format="MMM D, YYYY")]),
        html.Div(id="selected", style={"color": MUTED, "fontSize": ".85rem", "marginLeft": "auto"}),
    ]),
    html.Div(id="kpis", className="kpis"),
    html.Div(className="grid", children=[graph("perf"), graph("dist")]),
    html.Div(className="grid", children=[graph("volume"), graph("drawdown")]),
    html.Div(className="grid", children=[graph("corr"), graph("vol")]),
    html.Div(id="insight", className="card insight"),
    html.Footer(id="foot"),
])


def prepare(companies, start, end):
    df, source = load_data()
    d = df[(df["Ticker"].isin(companies or [])) & (df["Date"] >= start) & (df["Date"] <= end)]
    return d, source


@app.callback(
    Output("perf", "figure"), Output("dist", "figure"), Output("volume", "figure"),
    Output("drawdown", "figure"), Output("corr", "figure"), Output("vol", "figure"),
    Output("kpis", "children"), Output("insight", "children"), Output("selected", "children"),
    Output("foot", "children"),
    Input("companies", "value"), Input("dates", "start_date"), Input("dates", "end_date"),
)
def update(companies, start, end):
    d, source = prepare(companies, start, end)
    msg = empty_fig("Select at least one company and a valid date range")
    if d.empty or d["Ticker"].nunique() < 1:
        return (msg,) * 6 + ([], "", "", "")
    px = d.pivot(index="Date", columns="Ticker", values="Close").dropna()
    if len(px) < 3:
        return (msg,) * 6 + ([], "", "", "")
    tick = list(px.columns)
    rets = px.pct_change().dropna()
    norm = px / px.iloc[0] * 100

    # 1 normalized performance
    f1 = go.Figure([go.Scatter(x=norm.index, y=norm[t], name=NAMES[t], line=dict(color=COLORS[t], width=2))
                    for t in tick])
    f1.add_hline(y=100, line_dash="dot", line_color=MUTED)
    style(f1, "Normalized Performance (start of range = 100)", "Index level (start = 100, log scale)").update_yaxes(type="log")

    # 2 daily-return distribution
    f2 = go.Figure([go.Violin(y=rets[t] * 100, name=NAMES[t], box_visible=True, meanline_visible=True,
                              line_color=COLORS[t], fillcolor=COLORS[t], opacity=0.55, points=False)
                    for t in tick])
    style(f2, "Daily Return Distribution", "Daily return (%)", xtitle="").update_layout(showlegend=False)

    # 3 trading volume (monthly average, millions)
    v = d.pivot(index="Date", columns="Ticker", values="Volume")[tick]
    vm = (v.resample("MS").mean() / 1e6)
    f3 = go.Figure([go.Bar(x=vm.index, y=vm[t], name=NAMES[t], marker_color=COLORS[t]) for t in tick])
    style(f3, "Average Daily Trading Volume by Month", "Shares traded per day (millions)").update_layout(barmode="group")

    # 4 drawdown
    dd = (px / px.cummax() - 1) * 100
    f4 = go.Figure([go.Scatter(x=dd.index, y=dd[t], name=NAMES[t], fill="tozeroy",
                               line=dict(color=COLORS[t], width=1.5)) for t in tick])
    style(f4, "Drawdown from Previous Peak", "Decline from peak (%)")

    # 5 correlation heatmap
    if len(tick) >= 2:
        c = rets.corr()
        f5 = go.Figure(go.Heatmap(z=c.values, x=[NAMES[t] for t in c.columns], y=[NAMES[t] for t in c.index],
                                  zmin=-1, zmax=1, colorscale="Purples", text=c.round(2).values,
                                  texttemplate="%{text}", colorbar=dict(title="ρ")))
        style(f5, "Daily-Return Correlation (−1 to +1)", xtitle="")
    else:
        f5 = empty_fig("Select 2+ companies for correlation")

    # 6 rolling volatility
    win = 30 if len(rets) > 40 else max(5, len(rets) // 2)
    rv = rets.rolling(win).std() * np.sqrt(252) * 100
    f6 = go.Figure([go.Scatter(x=rv.index, y=rv[t], name=NAMES[t], line=dict(color=COLORS[t], width=2))
                    for t in tick])
    style(f6, f"Rolling {win}-Day Annualized Volatility", "Annualized volatility (%)")

    # KPIs & insights
    tot = (px.iloc[-1] / px.iloc[0] - 1) * 100
    vol = rets.std() * np.sqrt(252) * 100
    mdd = dd.min()
    kpis = [html.Div(className="card kpi", style={"borderColor": COLORS[t]}, children=[
        html.B(f"{NAMES[t]} ({t})"),
        html.Div(f"Total return {tot[t]:+.1f}%  •  Volatility {vol[t]:.1f}%  •  Max drawdown {mdd[t]:.1f}%")])
        for t in tick]
    best, worst = tot.idxmax(), tot.idxmin()
    hi_v, lo_v = vol.idxmax(), vol.idxmin()
    items = [
        f"Returns: {NAMES[best]} led the selected period at {tot[best]:+.1f}%, while {NAMES[worst]} "
        f"returned {tot[worst]:+.1f}%.",
        f"Risk: {NAMES[hi_v]} was the most volatile ({vol[hi_v]:.0f}% annualized) vs. {NAMES[lo_v]} "
        f"({vol[lo_v]:.0f}%); its wider return distribution and deeper drawdowns reflect that.",
    ]
    if len(tick) >= 2:
        cc = rets.corr().where(~np.eye(len(tick), dtype=bool)).stack()
        items.append(f"Co-movement: the most correlated pair is {NAMES[cc.idxmax()[0]]}/{NAMES[cc.idxmax()[1]]} "
                     f"(ρ={cc.max():.2f}); the least is {NAMES[cc.idxmin()[0]]}/{NAMES[cc.idxmin()[1]]} "
                     f"(ρ={cc.min():.2f}). Defense primes tend to move together; Palantir trades more like a growth/AI stock.")
    items.append("Volume: Palantir's retail-heavy share count means far more shares trade per day, but its price is "
                 "different, so compare volume as activity, not dollars. Price moves alone do not explain causes.")
    insight = [html.H3("What the charts reveal"), html.Ul([html.Li(i) for i in items])]
    sel = f"{', '.join(tick)} | {px.index[0]:%b %d, %Y} – {px.index[-1]:%b %d, %Y}"
    foot = f"Data: {source}, adjusted close; latest trading day {px.index[-1]:%b %d, %Y}. " \
           f"Educational use only — not investment advice."
    return f1, f2, f3, f4, f5, f6, kpis, insight, sel, foot


# Vercel / WSGI entry point
server = app.server
app_wsgi = server

if __name__ == "__main__":
    app.run(debug=False, port=8050)
