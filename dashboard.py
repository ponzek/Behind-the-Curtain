"""Behind the Curtain: Data, Defense & Dollars
Interactive Plotly Dash dashboard comparing Palantir (PLTR), Lockheed Martin (LMT) and RTX.
Soft, whimsical redesign; layout inspired by the Kean Office of Institutional Research dashboard.
Developed for CPS*5745 by Karina Ponze.
"""
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, ctx, dcc, html, no_update

from update_data import TICKERS, fetch_ticker

DATA_FILE = Path(__file__).parent / "data" / "prices.csv"
CACHE_SECONDS = 6 * 3600
NAMES = {"PLTR": "Palantir", "LMT": "Lockheed Martin", "RTX": "RTX"}
EMOJI = {"PLTR": "🔮", "LMT": "🦋", "RTX": "🍑"}
COLORS = {"PLTR": "#b79cff", "LMT": "#6fd3c4", "RTX": "#ffa99b"}
INK, MUTED, GRID, CARD = "#5a4a78", "#9a8db5", "rgba(154,141,181,0.18)", "#ffffff"
FONT = "Quicksand, 'Trebuchet MS', sans-serif"
QUICK = {"1M": 1, "3M": 3, "6M": 6, "1Y": 12, "2Y": 24, "5Y": 60}

_cache = {"ts": 0.0, "df": None, "source": ""}


def load_data():
    """Latest data from Yahoo Finance (cached); falls back to the bundled snapshot."""
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


def style(fig, ytitle=None, xtitle=None, height=330, legend=True, hover="x unified"):
    fig.update_layout(
        paper_bgcolor=CARD, plot_bgcolor=CARD, font=dict(color=INK, family=FONT, size=13),
        height=height, margin=dict(l=55, r=15, t=15, b=40), hovermode=hover, showlegend=legend,
        legend=dict(orientation="h", y=-0.22, font=dict(color=MUTED)),
        hoverlabel=dict(bgcolor="#fff", font=dict(color=INK, family=FONT)),
    )
    fig.update_xaxes(gridcolor=GRID, title=xtitle, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, title=ytitle, zeroline=False, linecolor=GRID)
    return fig


def empty_fig(msg, height=330):
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(color=MUTED, size=14))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style(fig, height=height, legend=False)


CSS = """
:root{--ink:#5a4a78;--muted:#9a8db5;--pink:#ffd6e7;--lav:#e6dcff;--mint:#d3f4ec;--peach:#ffe4dc}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);font-family:Quicksand,'Trebuchet MS',sans-serif;min-height:100vh;
background:radial-gradient(circle at 8% 10%,#ffe4f1 0,transparent 35%),radial-gradient(circle at 92% 18%,#e3dcff 0,transparent 38%),
radial-gradient(circle at 50% 100%,#d6f5ee 0,transparent 45%),#fff8f4}
.wrap{max-width:1400px;margin:auto;padding:18px 22px 10px}
.banner{position:relative;overflow:hidden;border-radius:28px;padding:26px 34px;margin-bottom:16px;
background:linear-gradient(120deg,#c9b6ff 0%,#ffc2dd 55%,#ffd9c7 100%);box-shadow:0 12px 30px rgba(183,156,255,.35);
display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}
.banner h1{font-family:Fredoka,Quicksand,sans-serif;font-weight:600;font-size:2.4rem;margin:0;color:#fff;text-shadow:0 3px 0 rgba(122,92,190,.35)}
.banner p{margin:6px 0 0;color:#fff;font-weight:600;opacity:.95}
.badge{background:rgba(255,255,255,.85);border-radius:20px;padding:12px 20px;font-weight:700;text-align:right;line-height:1.5}
.sparkle{position:absolute;font-size:1.6rem;animation:float 5s ease-in-out infinite;opacity:.85}
@keyframes float{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-10px) rotate(12deg)}}
h2.page{font-family:Fredoka,sans-serif;font-weight:500;margin:6px 4px 10px;font-size:1.5rem}
.card{background:#fff;border-radius:24px;padding:14px 16px;box-shadow:0 8px 24px rgba(183,156,255,.22);
border:2px solid #f3ebff;transition:transform .25s,box-shadow .25s}
.card:hover{transform:translateY(-3px);box-shadow:0 14px 30px rgba(255,169,155,.28)}
.card h3{font-family:Fredoka,sans-serif;font-weight:500;margin:2px 4px 0;font-size:1.15rem}
.card .cap{margin:0 4px 4px;color:var(--muted);font-size:.82rem;font-weight:600}
.filters{display:flex;gap:26px;flex-wrap:wrap;align-items:flex-end;margin-bottom:16px;background:rgba(255,255,255,.75);backdrop-filter:blur(6px)}
.filters .lab{display:block;font-size:.72rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#8b78c9;margin-bottom:6px}
.cl label,.chips label{display:inline-flex;align-items:center;gap:6px;margin:0 8px 6px 0;padding:7px 14px;border-radius:999px;
font-weight:700;cursor:pointer;background:var(--lav);transition:all .2s}
.cl label:hover,.chips label:hover{transform:scale(1.06);background:var(--pink)}
.cl input,.chips input{accent-color:#b79cff}
.chips label{padding:6px 12px;background:var(--mint)}
.btn{border:0;border-radius:999px;padding:10px 20px;font-family:Fredoka,sans-serif;font-size:1rem;color:#fff;cursor:pointer;
background:linear-gradient(120deg,#b79cff,#ff9ec4);box-shadow:0 6px 14px rgba(183,156,255,.4);transition:transform .2s}
.btn:hover{transform:scale(1.07) rotate(-2deg)}
.main{display:grid;grid-template-columns:1fr 1.7fr 1fr;gap:16px;margin-bottom:16px}
.col{display:flex;flex-direction:column;gap:16px}
.row2{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px;margin-bottom:16px}
.kpis{display:grid;grid-template-columns:1fr;gap:10px}
.kpi{border-radius:20px;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;font-weight:700}
.kpi big{font-family:Fredoka,sans-serif;font-size:1.6rem;font-weight:500}
.kpi small{display:block;color:var(--muted);font-weight:600}
table.t{width:100%;border-collapse:separate;border-spacing:0 6px;font-size:.88rem}
table.t th{color:#8b78c9;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;text-align:right;padding:0 8px}
table.t th:first-child,table.t td:first-child{text-align:left}
table.t td{padding:9px 8px;text-align:right;font-weight:700;background:#faf6ff}
table.t td:first-child{border-radius:14px 0 0 14px}table.t td:last-child{border-radius:0 14px 14px 0}
.insight ul{margin:6px 0 0;padding-left:20px;line-height:1.7;font-weight:600}
footer.foot{text-align:center;color:var(--muted);padding:14px;font-size:.88rem;font-weight:600}
.DateInput_input{font-family:Quicksand!important;font-weight:700!important;color:#5a4a78!important;border-radius:999px!important;background:#faf6ff!important}
.DateRangePickerInput{border-radius:999px!important;border:2px solid #e6dcff!important;overflow:hidden;background:#faf6ff!important}
.DateInput,.DateRangePickerInput_arrow{background:#faf6ff!important}
.CalendarDay__selected,.CalendarDay__selected:hover{background:#b79cff!important;border:1px double #b79cff!important}
.CalendarDay__selected_span{background:#e6dcff!important;border:1px double #e6dcff!important;color:#5a4a78!important}
@media(max-width:1000px){.main{grid-template-columns:1fr}.banner h1{font-size:1.7rem}}
"""

app = Dash(__name__, title="Behind the Curtain: Data, Defense & Dollars")
app.index_string = (
    """<!DOCTYPE html><html lang="en"><head>{%metas%}<title>{%title%}</title>
<meta name="description" content="A soft, interactive comparison of Palantir, Lockheed Martin and RTX stock performance.">
{%favicon%}{%css%}
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&family=Quicksand:wght@500;600;700&display=swap" rel="stylesheet">
<style>"""
    + CSS
    + """</style></head><body>{%app_entry%}{%config%}{%scripts%}{%renderer%}</body></html>"""
)

_df0, _ = load_data()
MIN_D, MAX_D = _df0["Date"].min().date(), _df0["Date"].max().date()


def default_start(months=24):
    return max(MIN_D, (_df0["Date"].max() - pd.DateOffset(months=months)).date())


def card(title, caption, gid, extra=None, **kw):
    return html.Div(className="card", **kw, children=[
        html.H3(title), html.P(caption, className="cap"),
        dcc.Graph(id=gid, config={"displaylogo": False, "displayModeBar": False}), *(extra or [])])


app.layout = html.Div(className="wrap", children=[
    html.Header(className="banner", children=[
        html.Span("✨", className="sparkle", style={"left": "42%", "top": "10px"}),
        html.Span("☁️", className="sparkle", style={"right": "22%", "bottom": "6px", "animationDelay": "1s"}),
        html.Span("🌸", className="sparkle", style={"left": "26px", "bottom": "4px", "animationDelay": "2s"}),
        html.Div([
            html.H1("🎀 Behind the Curtain: Data, Defense & Dollars"),
            html.P("Palantir 🔮 vs. Lockheed Martin 🦋 vs. RTX 🍑  —  one software dreamer, two defense giants"),
        ]),
        html.Div(className="badge", children=[
            html.Div("Created by Karina Ponze 💜"), html.Div("Developed for CPS*5745")]),
    ]),
    html.H2("Stock Comparison — Latest Market Data At-a-Glance", className="page"),
    html.Div(className="card filters", children=[
        html.Div([html.Span("🏢 Companies", className="lab"),
                  dcc.Checklist(id="companies", className="cl", value=TICKERS, inline=True,
                                options=[{"label": f"{EMOJI[t]} {NAMES[t]} ({t})", "value": t} for t in TICKERS])]),
        html.Div([html.Span("📅 Date range", className="lab"),
                  dcc.DatePickerRange(id="dates", min_date_allowed=MIN_D, max_date_allowed=MAX_D,
                                      start_date=default_start(), end_date=MAX_D, display_format="MMM D, YYYY")]),
        html.Div([html.Span("⏳ Quick range", className="lab"),
                  dcc.RadioItems(id="quick", className="chips", value="2Y", inline=True,
                                 options=[{"label": k, "value": k} for k in QUICK])]),
        html.Button("↺ Reset", id="reset", className="btn", n_clicks=0),
        html.Div(id="selected", style={"marginLeft": "auto", "color": MUTED, "fontWeight": 700, "fontSize": ".85rem"}),
    ]),
    html.Div(className="main", children=[
        html.Div(className="col", children=[
            card("Total Return", "Who grew the most over your chosen dates? 🌱", "ret_bar"),
            card("Volatility", "How bumpy was the ride? (annualized %) 🎢", "vol_bar"),
        ]),
        html.Div(className="col", children=[
            card("Normalized Performance", "Everyone starts at 100 so share prices are fair to compare 🚀", "perf"),
            card("Trading Volume", "Average shares traded per day, by month 🫧", "volume"),
        ]),
        html.Div(className="col", children=[
            html.Div(className="card", children=[html.H3("Period Highlights"), html.Div(id="kpis", className="kpis")]),
            card("Dollar Volume Share", "Slices of the money changing hands 🍰", "donut"),
            card("Up Days vs Down Days", "Share of trading days in the green 🍀", "updown"),
        ]),
    ]),
    html.Div(className="row2", children=[
        card("Daily Return Distribution", "Wider shape = wilder days 🎈", "dist"),
        card("Drawdown from Peak", "How far each stock slid from its best moment 🌧️", "drawdown"),
        card("Return Correlation", "Closer to +1 means they dance together 💃", "corr"),
    ]),
    html.Div(className="card", children=[html.H3("Company Scorecard"), html.P("The numbers behind the pastel 🧁", className="cap"),
                                         html.Div(id="table")]),
    html.Div(className="card insight", style={"marginTop": "16px"}, children=[html.Div(id="insight")]),
    html.Footer(id="foot", className="foot"),
])


@app.callback(
    Output("companies", "value"), Output("dates", "start_date"), Output("dates", "end_date"), Output("quick", "value"),
    Input("reset", "n_clicks"), Input("quick", "value"), prevent_initial_call=True,
)
def controls(_, quick):
    if ctx.triggered_id == "reset":
        return TICKERS, default_start(), MAX_D, "2Y"
    if quick in QUICK:
        return no_update, default_start(QUICK[quick]), MAX_D, no_update
    return no_update, no_update, no_update, no_update


def pct(v):
    return f"{v:+.1f}%"


@app.callback(
    Output("ret_bar", "figure"), Output("vol_bar", "figure"), Output("perf", "figure"), Output("volume", "figure"),
    Output("donut", "figure"), Output("updown", "figure"), Output("dist", "figure"), Output("drawdown", "figure"),
    Output("corr", "figure"), Output("kpis", "children"), Output("table", "children"),
    Output("insight", "children"), Output("selected", "children"), Output("foot", "children"),
    Input("companies", "value"), Input("dates", "start_date"), Input("dates", "end_date"),
)
def update(companies, start, end):
    df, source = load_data()
    empty = (empty_fig("Pick a company and a date range 🌷"),) * 9 + ([], "", "", "", "")
    if not companies or not start or not end:
        return empty
    d = df[df["Ticker"].isin(companies) & (df["Date"] >= start) & (df["Date"] <= end)]
    px = d.pivot(index="Date", columns="Ticker", values="Close").dropna() if not d.empty else pd.DataFrame()
    if len(px) < 3:
        return empty
    tick = [t for t in TICKERS if t in px.columns]
    px = px[tick]
    rets = px.pct_change().dropna()
    norm = px / px.iloc[0] * 100
    label = lambda t: f"{EMOJI[t]} {NAMES[t]}"
    cols = [COLORS[t] for t in tick]

    tot = (px.iloc[-1] / px.iloc[0] - 1) * 100
    vol = rets.std() * np.sqrt(252) * 100
    dd = (px / px.cummax() - 1) * 100
    mdd = dd.min()

    # Horizontal bars (reference style): total return
    order = tot.sort_values().index
    f_ret = go.Figure(go.Bar(y=[label(t) for t in order], x=tot[order], orientation="h",
                             marker=dict(color=[COLORS[t] for t in order], cornerradius=12),
                             text=[pct(tot[t]) for t in order], textposition="outside", cliponaxis=False,
                             hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
    style(f_ret, xtitle="Total return over period (%)", height=250, legend=False, hover="closest")
    f_ret.update_layout(margin=dict(l=10, r=40, t=10, b=40))
    f_ret.update_xaxes(range=[min(0, tot.min()) * 1.3 - 5, max(0, tot.max()) * 1.35 + 5])

    order = vol.sort_values().index
    f_vol = go.Figure(go.Bar(y=[label(t) for t in order], x=vol[order], orientation="h",
                             marker=dict(color=[COLORS[t] for t in order], cornerradius=12),
                             text=[f"{vol[t]:.0f}%" for t in order], textposition="outside", cliponaxis=False,
                             hovertemplate="%{y}: %{x:.1f}%<extra></extra>"))
    style(f_vol, xtitle="Annualized volatility (%)", height=250, legend=False, hover="closest")
    f_vol.update_layout(margin=dict(l=10, r=40, t=10, b=40))
    f_vol.update_xaxes(range=[0, vol.max() * 1.25])

    # Normalized performance (line)
    f_perf = go.Figure([go.Scatter(x=norm.index, y=norm[t], name=label(t), line=dict(color=COLORS[t], width=3, shape="spline"))
                        for t in tick])
    f_perf.add_hline(y=100, line_dash="dot", line_color=MUTED)
    style(f_perf, "Index (start of range = 100, log scale)", height=360).update_yaxes(type="log")

    # Monthly average volume (grouped columns)
    v = d.pivot(index="Date", columns="Ticker", values="Volume")[tick]
    vm = v.resample("MS").mean() / 1e6
    f_volume = go.Figure([go.Bar(x=vm.index, y=vm[t], name=label(t), marker=dict(color=COLORS[t], cornerradius=6))
                          for t in tick])
    style(f_volume, "Shares per day (millions)", height=310).update_layout(barmode="group")

    # Dollar volume donut
    dv = (d.assign(DV=d["Close"] * d["Volume"]).groupby("Ticker")["DV"].sum().reindex(tick) / 1e9)
    f_donut = go.Figure(go.Pie(labels=[label(t) for t in tick], values=dv.values, hole=0.58, sort=False,
                               marker=dict(colors=cols, line=dict(color="#fff", width=4)),
                               textinfo="percent", hovertemplate="%{label}<br>$%{value:,.0f}B traded<extra></extra>"))
    style(f_donut, height=250, hover="closest")
    f_donut.update_layout(margin=dict(l=10, r=10, t=10, b=60), height=270,
                          legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.05, yanchor="top", font=dict(color=MUTED)))

    # Up vs down days donut-like (stacked horizontal 100% bars)
    up = (rets > 0).mean() * 100
    f_up = go.Figure([
        go.Bar(y=[label(t) for t in tick], x=[up[t] for t in tick], orientation="h", name="Up days",
               marker=dict(color="#a8e6cf"), text=[f"{up[t]:.0f}%" for t in tick], hovertemplate="%{x:.1f}% up<extra></extra>"),
        go.Bar(y=[label(t) for t in tick], x=[100 - up[t] for t in tick], orientation="h", name="Down days",
               marker=dict(color="#ffc2d1"), text=[f"{100 - up[t]:.0f}%" for t in tick], hovertemplate="%{x:.1f}% down<extra></extra>"),
    ])
    style(f_up, xtitle="% of trading days", height=290, hover="closest").update_layout(
        barmode="stack", margin=dict(l=10, r=10, t=45, b=60),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.02, yanchor="bottom", font=dict(color=MUTED)))
    f_up.update_xaxes(title_standoff=12, range=[0, 100])

    # Violin: daily-return distribution
    f_dist = go.Figure([go.Violin(y=rets[t] * 100, name=label(t), box_visible=True, meanline_visible=True,
                                  line_color=COLORS[t], fillcolor=COLORS[t], opacity=0.7, points=False) for t in tick])
    style(f_dist, "Daily return (%)", height=340, legend=False, hover="closest")

    # Drawdown
    f_dd = go.Figure([go.Scatter(x=dd.index, y=dd[t], name=label(t), fill="tozeroy", line=dict(color=COLORS[t], width=2))
                      for t in tick])
    style(f_dd, "Decline from previous peak (%)", height=340)

    # Correlation heatmap
    if len(tick) >= 2:
        c = rets.corr()
        f_corr = go.Figure(go.Heatmap(z=c.values, x=[label(t) for t in c.columns], y=[label(t) for t in c.index],
                                      zmin=-1, zmax=1, colorscale=[[0, "#ffd6e7"], [0.5, "#f5efff"], [1, "#9d7dff"]],
                                      text=c.round(2).values, texttemplate="%{text}", xgap=4, ygap=4,
                                      colorbar=dict(title="ρ", thickness=12)))
        style(f_corr, height=340, legend=False, hover="closest")
    else:
        f_corr = empty_fig("Pick 2+ companies to see correlation 💞", 340)

    kpis = [html.Div(className="kpi", style={"background": COLORS[t] + "40"}, children=[
        html.Div([html.B(label(t)), html.Small(f"Max drawdown {mdd[t]:.1f}%")]),
        html.Big(f"${px[t].iloc[-1]:,.0f}")]) for t in tick]
    kpis.append(html.Div(className="kpi", style={"background": "#f5efff"}, children=[
        html.Div([html.B("Trading days"), html.Small(f"{px.index[0]:%b %d} → {px.index[-1]:%b %d}")]), html.Big(f"{len(px)}")]))

    rows = [html.Tr([html.Td(f"{label(t)} ({t})"), html.Td(f"${px[t].iloc[0]:,.2f}"), html.Td(f"${px[t].iloc[-1]:,.2f}"),
                     html.Td(pct(tot[t]), style={"color": "#2fa88a" if tot[t] >= 0 else "#e0607e"}),
                     html.Td(f"{vol[t]:.1f}%"), html.Td(f"{mdd[t]:.1f}%"),
                     html.Td(f"{v[t].mean() / 1e6:,.1f}M")]) for t in tick]
    table = html.Table(className="t", children=[
        html.Thead(html.Tr([html.Th(h) for h in ["Company", "Start price", "End price", "Total return", "Volatility",
                                                  "Max drawdown", "Avg daily volume"]])), html.Tbody(rows)])

    best, worst, hi, lo = tot.idxmax(), tot.idxmin(), vol.idxmax(), vol.idxmin()
    items = [
        f"🌱 Returns: {NAMES[best]} grew the most ({pct(tot[best])}); {NAMES[worst]} came in at {pct(tot[worst])}.",
        f"🎢 Risk: {NAMES[hi]} was the bumpiest ({vol[hi]:.0f}% annualized volatility) while {NAMES[lo]} was calmest "
        f"({vol[lo]:.0f}%), showing in the wider violin shapes and deeper drawdowns.",
    ]
    if len(tick) >= 2:
        cc = rets.corr().where(~np.eye(len(tick), dtype=bool)).stack()
        a, b = cc.idxmax(); x, y = cc.idxmin()
        items.append(f"💃 Co-movement: {NAMES[a]} & {NAMES[b]} move most alike (ρ={cc.max():.2f}); "
                     f"{NAMES[x]} & {NAMES[y]} least (ρ={cc.min():.2f}). Defense primes tend to travel together, while "
                     f"Palantir behaves more like a growth/AI stock.")
    items.append("🫧 Volume is counted in shares, so a lower-priced stock can trade more shares for fewer dollars, "
                 "which is why the dollar-volume donut is shown too. Price charts show what happened, not why.")
    insight = [html.H3("What the charts reveal 🔍"), html.Ul([html.Li(i) for i in items])]
    sel = f"Showing: {', '.join(tick)} • {px.index[0]:%b %d, %Y} – {px.index[-1]:%b %d, %Y}"
    foot = (f"Data: {source}, adjusted close; latest trading day {px.index[-1]:%b %d, %Y}. Karina Ponze • "
            f"Developed for CPS*5745 • Educational use only, not investment advice. 🌸")
    return f_ret, f_vol, f_perf, f_volume, f_donut, f_up, f_dist, f_dd, f_corr, kpis, table, insight, sel, foot


# Vercel / WSGI entry point
server = app.server

if __name__ == "__main__":
    app.run(debug=False, port=8050)
