import html
import re
from datetime import date, timedelta

import streamlit as st

from rag import Planner

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="centered")


@st.cache_resource(show_spinner="Loading the AI model. This only happens once...")
def get_planner():
    return Planner()


# ----------------------------------------------------------------- styling
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Public+Sans:wght@400;500;600&display=swap');

:root{
  --ink:#14213D; --muted:#5B6678; --line:#DCE3E6; --paper:#FFFFFF;
  --teal:#0F766E; --teal-soft:#E3F2F0; --gold:#F2A900; --gold-soft:#FFF4D6;
}
html, body, .stApp, [data-testid="stAppViewContainer"]{
  background:#F3F6F6 !important; color:var(--ink);
  font-family:'Public Sans',system-ui,sans-serif;
}
[data-testid="stHeader"]{background:transparent;}
#MainMenu, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"]{display:none !important;}
.block-container{max-width:980px; padding-top:2.2rem; padding-bottom:4rem;}

/* hero */
.hero h1{
  font-family:'Bricolage Grotesque',sans-serif; font-weight:800;
  font-size:clamp(2rem,5vw,3.1rem); line-height:1.05; letter-spacing:-0.02em;
  color:var(--ink); margin:0 0 .6rem 0; padding:0;
}
.hero p{color:var(--muted); font-size:1.05rem; max-width:46ch; margin:0 0 1.6rem 0;}

/* form card */
[data-testid="stVerticalBlockBorderWrapper"]{
  background:var(--paper); border:1px solid var(--line) !important;
  border-radius:16px !important; box-shadow:0 1px 0 rgba(20,33,61,.03);
}
label, [data-testid="stWidgetLabel"] p{color:var(--ink) !important; font-weight:600; font-size:.88rem;}
[data-baseweb="select"] > div, [data-baseweb="input"]{border-radius:10px !important;}
.stButton > button, .stFormSubmitButton > button{
  background:var(--teal); color:#fff; border:0; border-radius:10px;
  padding:.7rem 1.4rem; font-weight:600; font-size:1rem; width:100%;
  font-family:'Public Sans',sans-serif;
}
.stButton > button:hover{background:#0B5F58; color:#fff;}
.stButton > button:focus-visible{outline:3px solid var(--gold); outline-offset:2px;}

/* result header */
.trip-head{margin:2.2rem 0 1rem 0;}
.trip-head h2{
  font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:clamp(1.6rem,4vw,2.3rem);
  letter-spacing:-0.015em; margin:0 0 .5rem 0; padding:0; color:var(--ink);
}
.chips{display:flex; gap:.5rem; flex-wrap:wrap;}
.chip{background:var(--paper); border:1px solid var(--line); border-radius:999px;
  padding:.25rem .8rem; font-size:.85rem; color:var(--muted); font-weight:500;}

/* stats */
.stats{display:grid; grid-template-columns:repeat(3,1fr); gap:.9rem; margin:1rem 0 1.4rem 0;}
.stat{background:var(--paper); border:1px solid var(--line); border-radius:14px; padding:1rem 1.15rem;}
.stat .k{color:var(--muted); font-size:.82rem; font-weight:500; margin-bottom:.25rem;}
.stat .v{font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:1.45rem; color:var(--ink);}
.stat .n{font-size:.82rem; margin-top:.2rem; font-weight:600;}
.ok{color:var(--teal);} .warn{color:#B45309;}
@media(max-width:700px){.stats{grid-template-columns:1fr;}}

/* tabs */
[data-baseweb="tab-list"]{gap:.4rem; border-bottom:1px solid var(--line);}
button[data-baseweb="tab"]{font-weight:600; color:var(--muted); padding:.6rem .9rem;}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--teal);}
[data-baseweb="tab-highlight"]{background:var(--teal) !important; height:3px !important;}

/* day ticket (the one memorable element) */
.ticket{display:flex; background:var(--paper); border:1px solid var(--line);
  border-radius:16px; margin:1rem 0; overflow:hidden;}
.stub{flex:0 0 110px; background:var(--teal); color:#fff; padding:1.1rem .6rem; text-align:center;
  display:flex; flex-direction:column; justify-content:center; align-items:center; position:relative;}
.stub .d{font-size:.85rem; opacity:.85; font-weight:500;}
.stub .num{font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:2.6rem; line-height:1;}
.stub .dt{margin-top:.5rem; font-size:.82rem; font-weight:600; background:rgba(255,255,255,.16);
  border-radius:999px; padding:.15rem .6rem;}
.perf{flex:0 0 0; border-left:2px dashed #B7C4C8; margin:.9rem 0;}
.slots{flex:1; padding:1rem 1.3rem;}
.slot{display:grid; grid-template-columns:92px 1fr; gap:.9rem; padding:.7rem 0; border-bottom:1px solid #EEF2F3;}
.slot:last-child{border-bottom:0;}
.slot .t{color:var(--teal); font-weight:700; font-size:.92rem;}
.slot .x{color:var(--ink); line-height:1.55; font-size:.97rem;}
@media(max-width:640px){
  .ticket{flex-direction:column;} .perf{border-left:0; border-top:2px dashed #B7C4C8; margin:0 .9rem;}
  .stub{flex-direction:row; gap:.8rem; flex-basis:auto; padding:.7rem;}
  .stub .dt{margin-top:0;} .slot{grid-template-columns:1fr; gap:.15rem;}
}

/* budget */
.panel{background:var(--paper); border:1px solid var(--line); border-radius:16px; padding:.6rem 1.4rem; margin-top:1rem;}
.brow{display:grid; grid-template-columns:1fr auto; gap:.3rem 1rem; padding:.9rem 0; border-bottom:1px solid #EEF2F3;}
.brow:last-child{border-bottom:0;}
.brow .n{font-weight:600;} .brow .a{font-weight:700; font-variant-numeric:tabular-nums;}
.bar{grid-column:1 / -1; height:8px; background:#EAF0F1; border-radius:99px; overflow:hidden;}
.bar i{display:block; height:100%; background:var(--teal); border-radius:99px;}
.btotal{display:flex; justify-content:space-between; padding:1rem 0; font-weight:800; font-size:1.1rem;}
.note{color:var(--muted); font-size:.85rem; margin:.8rem 0 0 0;}

/* hotels + tips */
.hotels{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:.9rem; margin-top:1rem;}
.hotel{background:var(--paper); border:1px solid var(--line); border-radius:14px; padding:1.1rem 1.2rem; border-top:4px solid var(--gold);}
.hotel .tier{color:var(--muted); font-size:.85rem; font-weight:600;}
.hotel .nm{font-family:'Bricolage Grotesque',sans-serif; font-weight:800; font-size:1.2rem; margin-top:.2rem;}
.tips{list-style:none; padding:0; margin:1rem 0 0 0;}
.tips li{background:var(--paper); border:1px solid var(--line); border-radius:12px;
  padding:.85rem 1.1rem .85rem 2.6rem; margin-bottom:.6rem; position:relative; line-height:1.5;}
.tips li::before{content:""; position:absolute; left:1.05rem; top:1.15rem; width:.7rem; height:.7rem;
  border-radius:50%; background:var(--gold);}
.empty{background:var(--gold-soft); border-radius:12px; padding:1rem 1.2rem; color:#7A5600;}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------- helpers
def esc(s):
    return html.escape(s or "")


def clean(line):
    return re.sub(r"\*+", "", line).strip(" #-•\t")


def to_int(s):
    digits = re.sub(r"[^\d]", "", s or "")
    return int(digits) if digits else None


def rupees(n):
    return "₹" + f"{n:,}" if n is not None else "-"


def section(text, name, others):
    m = re.search(rf"{name}\s*:?", text, re.I)
    if not m:
        return ""
    rest = text[m.end():]
    end = len(rest)
    for o in others:
        m2 = re.search(rf"\n[\s#*\-]*{o}\s*:?", rest, re.I)
        if m2:
            end = min(end, m2.start())
    return rest[:end].strip()


def parse(answer):
    best = re.search(r"Best Time to Visit\s*:?\**\s*(.+)", answer, re.I)
    best = clean(best.group(1)) if best else ""

    head_end = len(answer)
    for key in ("Trip Budget", "Tips"):
        m = re.search(rf"\n[\s#*\-]*{key}\s*:?", answer, re.I)
        if m:
            head_end = min(head_end, m.start())
    days_text = answer[:head_end]
    parts = re.split(r"(?im)^[\s#*]*Day\s*(\d+)\s*:?\**", days_text)
    days = []
    for i in range(1, len(parts) - 1, 2):
        slots, last = {}, None
        for raw in parts[i + 1].splitlines():
            ln = clean(raw)
            if not ln:
                continue
            m = re.match(r"(Morning|Afternoon|Evening)\s*:?\s*(.*)", ln, re.I)
            if m:
                last = m.group(1).capitalize()
                slots[last] = m.group(2).strip()
            elif last:
                slots[last] += " " + ln
            else:
                slots.setdefault("Plan", "")
                slots["Plan"] += (" " if slots["Plan"] else "") + ln
        days.append(slots)

    budget_txt = section(answer, "Trip Budget", ["Tips", "Hotels"])
    items, total, yours = [], None, None
    for raw in budget_txt.splitlines():
        ln = clean(raw)
        m = re.match(r"(.+?)\s*:\s*₹?\s*([\d,]+)", ln)
        if not m:
            continue
        name, amt = m.group(1).strip(), to_int(m.group(2))
        low = name.lower()
        if "total" in low:
            total = amt
        elif "your" in low:
            yours = amt
        else:
            items.append((name, amt))

    tips = [clean(l) for l in section(answer, "Tips", ["Hotels"]).splitlines() if clean(l)]
    hotels = []
    for raw in section(answer, "Hotels", ["zzzz"]).splitlines():
        ln = clean(raw)
        m = re.match(r"([A-Za-z ]+?)\s*:\s*(.+)", ln)
        if m:
            hotels.append((m.group(1).strip(), m.group(2).strip()))
    return dict(best=best, days=days, items=items, total=total, yours=yours, tips=tips, hotels=hotels)


def build_prompt(destination, days, trip_type, budget, start_date, end_date):
    return f"""
You are a professional travel planner.
Plan a {days} day {trip_type} trip to {destination}
with a budget of ₹{budget}.
Travel dates from {start_date} to {end_date}.

STRICTLY include these fields at the top:
Best Time to Visit: <Month> to <Month>
Estimated Budget: ₹<number>
Best Time to Visit MUST be in this format:Month to Month
Example: October to February
No extra words.

STRICTLY use this format:
Day 1:
- Morning:
- Afternoon:
- Evening:
Day 2:
- Morning:
- Afternoon:
- Evening:
Day 3:


- Trip Budget:
- Accommodation: ₹<number>
- Food & Activities: ₹<number>
- Transportation: ₹<number>
-------------------------------
- Total Estimated: ₹<number>
- Your Budget: ₹{budget}
-------------------------------
Tips:
- Tip 1
- Tip 2
- Tip 3
- Tip 4
(Give four to five tips)
Hotels:
Example-
(- Luxury: Taj
- Mid: Radisson)

EMOJI RULES:
- Use at most ONE emoji per line.
- Place emoji ONLY at the END of the line.
- Do NOT use emojis in headings.
- Do NOT use emojis in Trip Budget numbers.
- Use only relevant travel emojis.
"""


# ----------------------------------------------------------------- page
st.markdown(
    """<div class="hero"><h1>Plan your India trip in a minute</h1>
<p>Pick a place, set your budget, and get a day-by-day plan with costs, hotels and tips.</p></div>""",
    unsafe_allow_html=True,
)

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    destination = c1.selectbox("Where to?", ["Goa", "Kerala", "Rajasthan", "Delhi", "Himachal", "Tamil Nadu", "Kashmir"])
    days = c2.selectbox("How many days?", [1, 2, 3, 4, 5, 6, 7], index=2)
    trip_type = c3.selectbox("Trip style", ["Relaxation", "Adventure", "Couple", "Family", "Solo"])
    c4, c5 = st.columns([2, 1])
    budget = c4.slider("Budget (₹)", 5000, 50000, 15000, step=1000, format="₹%d")
    start_date = c5.date_input("Start date", date.today())
    end_date = start_date + timedelta(days=days - 1)
    generate = st.button("Create my itinerary")

if generate:
    prompt = build_prompt(destination, days, trip_type, budget, start_date, end_date)
    with st.spinner("Planning your trip. This takes a few seconds..."):
        try:
            answer = get_planner().answer(prompt)
            st.session_state["result"] = dict(
                answer=answer, destination=destination, days=days, trip_type=trip_type,
                budget=budget, start=start_date, end=end_date,
            )
        except Exception as e:
            st.session_state.pop("result", None)
            st.error(f"We couldn't create the plan: {e}")

res = st.session_state.get("result")
if res:
    p = parse(res["answer"])
    if not p["days"]:
        st.markdown("<div class='empty'>We couldn't read the plan's layout, so here is the full text.</div>", unsafe_allow_html=True)
        st.markdown(res["answer"])
    else:
        n = res["days"]
        st.markdown(
            f"""<div class="trip-head"><h2>{n} {'day' if n == 1 else 'days'} in {esc(res['destination'])}</h2>
<div class="chips"><span class="chip">{esc(res['trip_type'])}</span>
<span class="chip">{res['start'].strftime('%d %b')} to {res['end'].strftime('%d %b %Y')}</span>
<span class="chip">Budget {rupees(res['budget'])}</span></div></div>""",
            unsafe_allow_html=True,
        )

        total = p["total"]
        if total is None:
            diff_html = ""
        elif total <= res["budget"]:
            diff_html = f"<div class='n ok'>{rupees(res['budget'] - total)} under your budget</div>"
        else:
            diff_html = f"<div class='n warn'>{rupees(total - res['budget'])} over your budget</div>"
        st.markdown(
            f"""<div class="stats">
<div class="stat"><div class="k">Best time to visit</div><div class="v">{esc(p['best']) or '-'}</div></div>
<div class="stat"><div class="k">Estimated cost</div><div class="v">{rupees(total)}</div>{diff_html}</div>
<div class="stat"><div class="k">Trip length</div><div class="v">{n} {'day' if n == 1 else 'days'}</div></div>
</div>""",
            unsafe_allow_html=True,
        )

        t_plan, t_budget, t_hotels, t_tips = st.tabs(["Itinerary", "Budget", "Hotels", "Tips"])

        with t_plan:
            for i, slots in enumerate(p["days"]):
                d = res["start"] + timedelta(days=i)
                rows = "".join(
                    f"<div class='slot'><div class='t'>{esc(k)}</div><div class='x'>{esc(v)}</div></div>"
                    for k, v in slots.items() if v
                )
                st.markdown(
                    f"""<div class="ticket"><div class="stub"><div class="d">Day</div><div class="num">{i + 1}</div>
<div class="dt">{d.strftime('%a, %d %b')}</div></div><div class="perf"></div><div class="slots">{rows}</div></div>""",
                    unsafe_allow_html=True,
                )

        with t_budget:
            if p["items"]:
                top = max(a for _, a in p["items"] if a) or 1
                rows = "".join(
                    f"<div class='brow'><div class='n'>{esc(nm)}</div><div class='a'>{rupees(a)}</div>"
                    f"<div class='bar'><i style='width:{int((a or 0) / top * 100)}%'></i></div></div>"
                    for nm, a in p["items"]
                )
                tot = f"<div class='btotal'><span>Total estimate</span><span>{rupees(total)}</span></div>" if total else ""
                st.markdown(f"<div class='panel'>{rows}{tot}</div>", unsafe_allow_html=True)
                st.markdown("<p class='note'>Costs can change with the season and the number of travellers.</p>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='empty'>No budget breakdown came back this time. Try creating the plan again.</div>", unsafe_allow_html=True)

        with t_hotels:
            if p["hotels"]:
                cards = "".join(
                    f"<div class='hotel'><div class='tier'>{esc(t)}</div><div class='nm'>{esc(h)}</div></div>"
                    for t, h in p["hotels"]
                )
                st.markdown(f"<div class='hotels'>{cards}</div>", unsafe_allow_html=True)
                st.markdown("<p class='note'>Prices and availability change with the season. Check before you book.</p>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='empty'>No hotel suggestions came back this time.</div>", unsafe_allow_html=True)

        with t_tips:
            if p["tips"]:
                st.markdown("<ul class='tips'>" + "".join(f"<li>{esc(t)}</li>" for t in p["tips"]) + "</ul>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='empty'>No tips came back this time.</div>", unsafe_allow_html=True)
