from service.Connection import db
from models.Updates import base_update
from models.Timings import base_timing
from models.Zones import base_zone
from models.Report import base_report

base_update.metadata.create_all(db)
base_timing.metadata.create_all(db)
base_zone.metadata.create_all(db)
base_report.metadata.create_all(db)
