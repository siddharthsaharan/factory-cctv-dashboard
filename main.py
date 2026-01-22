# from fastapi import FastAPI, Depends
# from sqlalchemy.orm import Session
# from database import SessionLocal, engine
# from models import Base, Event
# from schemas import EventSchema

# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="CCTV Event Ingestion API")

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.post("/cctv/events")
# def ingest_event(event: EventSchema, db: Session = Depends(get_db)):
#     db_event = Event(**event.dict())
#     db.add(db_event)
#     db.commit()
#     return {"status": "stored"}

# # (your existing code is above)

# from datetime import datetime

# @app.get("/metrics/workers")
# def worker_metrics(db: Session = Depends(get_db)):
#     events = db.query(Event).order_by(Event.timestamp).all()

#     metrics = {}

#     for e in events:
#         if e.worker_id not in metrics:
#             metrics[e.worker_id] = {
#                 "working_time": 0,
#                 "idle_time": 0,
#                 "units": 0,
#                 "last_time": e.timestamp,
#                 "last_state": e.event_type
#             }

#         m = metrics[e.worker_id]

#         diff = (e.timestamp - m["last_time"]).total_seconds() / 60

#         if m["last_state"] == "working":
#             m["working_time"] += diff
#         elif m["last_state"] == "idle":
#             m["idle_time"] += diff

#         if e.event_type == "product_count":
#             m["units"] += e.count

#         m["last_time"] = e.timestamp
#         m["last_state"] = e.event_type

#     result = []
#     for k, v in metrics.items():
#         total = v["working_time"] + v["idle_time"]
#         util = (v["working_time"] / total) * 100 if total > 0 else 0

#         result.append({
#             "worker_id": k,
#             "working_minutes": round(v["working_time"], 2),
#             "idle_minutes": round(v["idle_time"], 2),
#             "utilization": round(util, 2),
#             "units_produced": v["units"]
#         })


#     return result


# from fastapi.responses import HTMLResponse

# @app.get("/")
# def dashboard():
#     return HTMLResponse("""
#     <html>
#     <head>
#         <title>Factory Dashboard (Live)</title>
#         <style>
#             body { font-family: Arial; padding: 20px; }
#             table { border-collapse: collapse; width: 100%; margin-top: 20px; }
#             th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
#             th { background: #f2f2f2; }
#             .card { border: 1px solid #ccc; padding: 10px; margin: 10px; display: inline-block; }
#         </style>
#     </head>
#     <body>
#         <h2>Factory Dashboard (Live)</h2>

#         <div id="factory"></div>

#         <h3>Worker Metrics</h3>
#         <table>
#             <thead>
#                 <tr>
#                     <th>Worker</th>
#                     <th>Working</th>
#                     <th>Idle</th>
#                     <th>Utilization %</th>
#                     <th>Units</th>
#                 </tr>
#             </thead>
#             <tbody id="workers"></tbody>
#         </table>

#         <h3>Workstation Metrics</h3>
#         <table>
#             <thead>
#                 <tr>
#                     <th>Station</th>
#                     <th>Occupancy</th>
#                     <th>Units</th>
#                 </tr>
#             </thead>
#             <tbody id="stations"></tbody>
#         </table>

#         <script>
#             async function loadData() {

#                 // FACTORY
#                 const f = await fetch('/metrics/factory').then(r => r.json());
#                 document.getElementById("factory").innerHTML = `
#                     <div class='card'>Total Units: ${f.total_units_produced}</div>
#                     <div class='card'>Avg Utilization: ${f["average_utilization_%"]}%</div>
#                     <div class='card'>Working Minutes: ${f.total_working_minutes}</div>
#                 `;

#                 // WORKERS
#                 const workers = await fetch('/metrics/workers').then(r => r.json());
#                 const wbody = document.getElementById("workers");
#                 wbody.innerHTML = "";
#                 workers.forEach(w => {
#                     wbody.innerHTML += `
#                         <tr>
#                             <td>${w.worker_id}</td>
#                             <td>${w.working_minutes}</td>
#                             <td>${w.idle_minutes}</td>
#                             <td>${w["utilization_%"]}</td>
#                             <td>${w.units_produced}</td>
#                         </tr>`;
#                 });

#                 // STATIONS
#                 const stations = await fetch('/metrics/workstations').then(r => r.json());
#                 const sbody = document.getElementById("stations");
#                 sbody.innerHTML = "";
#                 stations.forEach(s => {
#                     sbody.innerHTML += `
#                         <tr>
#                             <td>${s.station_id}</td>
#                             <td>${s.occupancy_minutes}</td>
#                             <td>${s.units_produced}</td>
#                         </tr>`;
#                 });
#             }

#             // 🔥 LIVE REFRESH EVERY 2 SECONDS
#             setInterval(loadData, 2000);
#             loadData();
#         </script>
#     </body>
#     </html>
#     """)










# @app.get("/metrics/factory")
# def factory_metrics(db: Session = Depends(get_db)):
#     workers = worker_metrics(db)

#     total_units = sum(w["units_produced"] for w in workers)
#     avg_util = sum(w["utilization_%"] for w in workers) / len(workers)

#     total_working = sum(w["working_minutes"] for w in workers)

#     return {
#         "total_units_produced": total_units,
#         "average_utilization_%": round(avg_util, 2),
#         "total_working_minutes": round(total_working, 2)
#     }


# @app.get("/metrics/workstations")
# def workstation_metrics(db: Session = Depends(get_db)):
#     events = db.query(Event).order_by(Event.timestamp).all()
#     metrics = {}

#     for e in events:
#         sid = e.workstation_id
#         if sid not in metrics:
#             metrics[sid] = {
#                 "working_time": 0,
#                 "units": 0,
#                 "last_time": e.timestamp,
#                 "last_state": e.event_type
#             }

#         m = metrics[sid]
#         diff = (e.timestamp - m["last_time"]).total_seconds() / 60

#         if m["last_state"] == "working":
#             m["working_time"] += diff

#         if e.event_type == "product_count":
#             m["units"] += e.count

#         m["last_time"] = e.timestamp
#         m["last_state"] = e.event_type

#     result = []
#     for k, v in metrics.items():
#         result.append({
#             "station_id": k,
#             "occupancy_minutes": round(v["working_time"], 2),
#             "units_produced": v["units"]
#         })

#     return result








# from fastapi import FastAPI, Depends
# from fastapi.responses import HTMLResponse
# from sqlalchemy.orm import Session
# from datetime import datetime
# from typing import List

# from database import SessionLocal, engine
# from models import Base, Event
# from schemas import EventSchema

# # -------------------- DB INIT --------------------
# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="AI CCTV Productivity Dashboard")

# # -------------------- DB DEP --------------------
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # -------------------- EVENT INGESTION --------------------
# @app.post("/cctv/events")
# def ingest_event(event: EventSchema, db: Session = Depends(get_db)):
#     db_event = Event(**event.dict())
#     db.add(db_event)
#     db.commit()
#     return {"status": "stored"}

# # -------------------- METRIC HELPERS --------------------
# def compute_worker_metrics(events: List[Event]):
#     metrics = {}

#     for e in events:
#         wid = e.worker_id

#         if wid not in metrics:
#             metrics[wid] = {
#                 "working_time": 0.0,
#                 "idle_time": 0.0,
#                 "units": 0,
#                 "last_time": e.timestamp,
#                 "last_state": e.event_type
#             }
#             continue

#         m = metrics[wid]
#         diff = (e.timestamp - m["last_time"]).total_seconds() / 60

#         if m["last_state"] == "working":
#             m["working_time"] += diff
#         elif m["last_state"] == "idle":
#             m["idle_time"] += diff
#         # absent is ignored by design

#         if e.event_type == "product_count":
#             m["units"] += e.count or 0

#         m["last_time"] = e.timestamp
#         m["last_state"] = e.event_type

#     result = []
#     for wid, m in metrics.items():
#         total = m["working_time"] + m["idle_time"]
#         util = (m["working_time"] / total) * 100 if total > 0 else 0

#         result.append({
#             "worker_id": wid,
#             "working_minutes": round(m["working_time"], 2),
#             "idle_minutes": round(m["idle_time"], 2),
#             "utilization_pct": round(util, 2),
#             "units_produced": m["units"]
#         })

#     return result


# def compute_workstation_metrics(events: List[Event]):
#     metrics = {}

#     for e in events:
#         sid = e.workstation_id

#         if sid not in metrics:
#             metrics[sid] = {
#                 "working_time": 0.0,
#                 "units": 0,
#                 "last_time": e.timestamp,
#                 "last_state": e.event_type
#             }
#             continue

#         m = metrics[sid]
#         diff = (e.timestamp - m["last_time"]).total_seconds() / 60

#         if m["last_state"] == "working":
#             m["working_time"] += diff

#         if e.event_type == "product_count":
#             m["units"] += e.count or 0

#         m["last_time"] = e.timestamp
#         m["last_state"] = e.event_type

#     return [
#         {
#             "station_id": sid,
#             "occupancy_minutes": round(m["working_time"], 2),
#             "units_produced": m["units"]
#         }
#         for sid, m in metrics.items()
#     ]

# # -------------------- METRIC ROUTES --------------------
# @app.get("/metrics/workers")
# def worker_metrics(db: Session = Depends(get_db)):
#     events = db.query(Event).order_by(Event.timestamp).all()
#     return compute_worker_metrics(events)


# @app.get("/metrics/workstations")
# def workstation_metrics(db: Session = Depends(get_db)):
#     events = db.query(Event).order_by(Event.timestamp).all()
#     return compute_workstation_metrics(events)


# @app.get("/metrics/factory")
# def factory_metrics(db: Session = Depends(get_db)):
#     events = db.query(Event).order_by(Event.timestamp).all()

#     workers = compute_worker_metrics(events)

#     total_units = sum(w["units_produced"] for w in workers)
#     total_working = sum(w["working_minutes"] for w in workers)

#     avg_util = (
#         sum(w["utilization_pct"] for w in workers) / len(workers)
#         if workers else 0
#     )

#     return {
#         "total_units_produced": total_units,
#         "total_working_minutes": round(total_working, 2),
#         "average_utilization_pct": round(avg_util, 2)
#     }

# # -------------------- SIMPLE SEED API --------------------
# @app.post("/seed")
# def seed_data(db: Session = Depends(get_db)):
#     db.query(Event).delete()

#     now = datetime.utcnow()
#     sample = [
#         Event(timestamp=now, worker_id="W1", workstation_id="S1", event_type="working", confidence=0.95, count=0),
#         Event(timestamp=now, worker_id="W2", workstation_id="S2", event_type="working", confidence=0.92, count=0),
#         Event(timestamp=now, worker_id="W1", workstation_id="S1", event_type="product_count", confidence=0.90, count=3),
#     ]

#     db.add_all(sample)
#     db.commit()
#     return {"status": "seeded"}

# # -------------------- DASHBOARD --------------------
# @app.get("/")
# def dashboard():
#     return HTMLResponse("""
#     <html>
#     <head>
#         <title>Factory Productivity Dashboard</title>
#         <style>
#             body { font-family: Arial; padding: 20px; }
#             table { border-collapse: collapse; width: 100%; margin-top: 20px; }
#             th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
#             th { background: #f2f2f2; }
#             .card { border: 1px solid #ccc; padding: 10px; margin: 10px; display: inline-block; }
#         </style>
#     </head>
#     <body>
#         <h2>Factory Productivity Dashboard</h2>

#         <div id="factory"></div>

#         <h3>Workers</h3>
#         <table>
#             <thead>
#                 <tr>
#                     <th>Worker</th>
#                     <th>Working</th>
#                     <th>Idle</th>
#                     <th>Utilization %</th>
#                     <th>Units</th>
#                 </tr>
#             </thead>
#             <tbody id="workers"></tbody>
#         </table>

#         <h3>Workstations</h3>
#         <table>
#             <thead>
#                 <tr>
#                     <th>Station</th>
#                     <th>Occupancy</th>
#                     <th>Units</th>
#                 </tr>
#             </thead>
#             <tbody id="stations"></tbody>
#         </table>

#         <script>
#             async function loadData() {

#                 const f = await fetch('/metrics/factory').then(r => r.json());
#                 document.getElementById("factory").innerHTML = `
#                     <div class='card'>Total Units: ${f.total_units_produced}</div>
#                     <div class='card'>Avg Utilization: ${f.average_utilization_pct}%</div>
#                     <div class='card'>Working Minutes: ${f.total_working_minutes}</div>
#                 `;

#                 const workers = await fetch('/metrics/workers').then(r => r.json());
#                 const wbody = document.getElementById("workers");
#                 wbody.innerHTML = "";
#                 workers.forEach(w => {
#                     wbody.innerHTML += `
#                         <tr>
#                             <td>${w.worker_id}</td>
#                             <td>${w.working_minutes}</td>
#                             <td>${w.idle_minutes}</td>
#                             <td>${w.utilization_pct}</td>
#                             <td>${w.units_produced}</td>
#                         </tr>`;
#                 });

#                 const stations = await fetch('/metrics/workstations').then(r => r.json());
#                 const sbody = document.getElementById("stations");
#                 sbody.innerHTML = "";
#                 stations.forEach(s => {
#                     sbody.innerHTML += `
#                         <tr>
#                             <td>${s.station_id}</td>
#                             <td>${s.occupancy_minutes}</td>
#                             <td>${s.units_produced}</td>
#                         </tr>`;
#                 });
#             }

#             setInterval(loadData, 2000);
#             loadData();
#         </script>
#     </body>
#     </html>
#     """)









from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import SessionLocal, engine
from models import Base, Event
from schemas import EventSchema

# -------------------- INIT --------------------
Base.metadata.create_all(bind=engine)
app = FastAPI(title="AI-Powered Worker Productivity Dashboard")

# -------------------- DB DEP --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- EVENT INGESTION --------------------
@app.post("/cctv/events")
def ingest_event(event: EventSchema, db: Session = Depends(get_db)):
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    return {"status": "stored"}

# -------------------- METRIC HELPERS --------------------
def compute_worker_metrics(events: List[Event]):
    metrics = {}

    for e in events:
        wid = e.worker_id

        if wid not in metrics:
            metrics[wid] = {
                "working_time": 0.0,
                "idle_time": 0.0,
                "units": 0,
                "last_time": e.timestamp,
                "last_state": e.event_type
            }
            continue

        m = metrics[wid]
        diff = (e.timestamp - m["last_time"]).total_seconds() / 60

        if m["last_state"] == "working":
            m["working_time"] += diff
        elif m["last_state"] == "idle":
            m["idle_time"] += diff
        # absent is ignored

        if e.event_type == "product_count":
            m["units"] += e.count or 0

        m["last_time"] = e.timestamp
        m["last_state"] = e.event_type

    result = []
    for wid, m in metrics.items():
        total = m["working_time"] + m["idle_time"]
        util = (m["working_time"] / total) * 100 if total > 0 else 0
        uph = (m["units"] / (m["working_time"] / 60)) if m["working_time"] > 0 else 0

        result.append({
            "worker_id": wid,
            "working_minutes": round(m["working_time"], 2),
            "idle_minutes": round(m["idle_time"], 2),
            "utilization_pct": round(util, 2),
            "units_produced": m["units"],
            "units_per_hour": round(uph, 2)
        })

    return result


def compute_workstation_metrics(events: List[Event]):
    metrics = {}

    for e in events:
        sid = e.workstation_id

        if sid not in metrics:
            metrics[sid] = {
                "working_time": 0.0,
                "units": 0,
                "last_time": e.timestamp,
                "last_state": e.event_type
            }
            continue

        m = metrics[sid]
        diff = (e.timestamp - m["last_time"]).total_seconds() / 60

        if m["last_state"] == "working":
            m["working_time"] += diff

        if e.event_type == "product_count":
            m["units"] += e.count or 0

        m["last_time"] = e.timestamp
        m["last_state"] = e.event_type

    return [
        {
            "station_id": sid,
            "occupancy_minutes": round(m["working_time"], 2),
            "units_produced": m["units"]
        }
        for sid, m in metrics.items()
    ]

# -------------------- METRIC ROUTES --------------------
@app.get("/metrics/workers")
def worker_metrics(db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.timestamp).all()
    return compute_worker_metrics(events)


@app.get("/metrics/workstations")
def workstation_metrics(db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.timestamp).all()
    return compute_workstation_metrics(events)


@app.get("/metrics/factory")
def factory_metrics(db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.timestamp).all()
    workers = compute_worker_metrics(events)

    total_units = sum(w["units_produced"] for w in workers)
    total_working = sum(w["working_minutes"] for w in workers)
    avg_util = sum(w["utilization_pct"] for w in workers) / len(workers) if workers else 0

    return {
        "total_units_produced": total_units,
        "total_working_minutes": round(total_working, 2),
        "average_utilization_pct": round(avg_util, 2)
    }

# -------------------- SEED API --------------------
@app.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    db.query(Event).delete()

    now = datetime.utcnow()
    sample = [
        Event(timestamp=now, worker_id="W1", workstation_id="S1", event_type="working", confidence=0.95, count=0),
        Event(timestamp=now, worker_id="W1", workstation_id="S1", event_type="product_count", confidence=0.92, count=5),
        Event(timestamp=now, worker_id="W2", workstation_id="S2", event_type="working", confidence=0.94, count=0),
    ]

    db.add_all(sample)
    db.commit()
    return {"status": "seeded"}

# -------------------- DASHBOARD --------------------
@app.get("/")
def dashboard():
    return HTMLResponse("""
    <html>
    <head>
        <title>Factory Productivity Dashboard</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
            th { background: #f2f2f2; }
            .card { border: 1px solid #ccc; padding: 10px; margin: 10px; display: inline-block; }
        </style>
    </head>
    <body>
        <h2>Factory Productivity Dashboard</h2>

        <label>
            Time Unit:
            <select id="unit" onchange="loadData()">
                <option value="minutes">Minutes</option>
                <option value="hours">Hours</option>
            </select>
        </label>

        <div id="factory"></div>

        <h3>Workers</h3>
        <table>
            <thead>
                <tr>
                    <th>Worker</th>
                    <th>Working</th>
                    <th>Idle</th>
                    <th>Utilization %</th>
                    <th>Units</th>
                    <th>Units / Hour</th>
                </tr>
            </thead>
            <tbody id="workers"></tbody>
        </table>

        <h3>Workstations</h3>
        <table>
            <thead>
                <tr>
                    <th>Station</th>
                    <th>Occupancy</th>
                    <th>Units</th>
                </tr>
            </thead>
            <tbody id="stations"></tbody>
        </table>

        <script>
            async function loadData() {
                const unit = document.getElementById("unit").value;
                const factor = unit === "hours" ? 1/60 : 1;

                const f = await fetch('/metrics/factory').then(r => r.json());
                document.getElementById("factory").innerHTML = `
                    <div class='card'>Total Units: ${f.total_units_produced}</div>
                    <div class='card'>Avg Utilization: ${f.average_utilization_pct}%</div>
                    <div class='card'>Working Time: ${(f.total_working_minutes * factor).toFixed(2)} ${unit}</div>
                `;

                const workers = await fetch('/metrics/workers').then(r => r.json());
                const wbody = document.getElementById("workers");
                wbody.innerHTML = "";
                workers.forEach(w => {
                    wbody.innerHTML += `
                        <tr>
                            <td>${w.worker_id}</td>
                            <td>${(w.working_minutes * factor).toFixed(2)}</td>
                            <td>${(w.idle_minutes * factor).toFixed(2)}</td>
                            <td>${w.utilization_pct}</td>
                            <td>${w.units_produced}</td>
                            <td>${w.units_per_hour}</td>
                        </tr>`;
                });

                const stations = await fetch('/metrics/workstations').then(r => r.json());
                const sbody = document.getElementById("stations");
                sbody.innerHTML = "";
                stations.forEach(s => {
                    sbody.innerHTML += `
                        <tr>
                            <td>${s.station_id}</td>
                            <td>${(s.occupancy_minutes * factor).toFixed(2)}</td>
                            <td>${s.units_produced}</td>
                        </tr>`;
                });
            }

            setInterval(loadData, 2000);
            loadData();
        </script>
    </body>
    </html>
    """)
