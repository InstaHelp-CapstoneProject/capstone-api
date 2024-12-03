from marshmallow import Schema, fields, ValidationError, EXCLUDE
from marshmallow.decorators import validates
from sqlalchemy.orm import Session
from app.models.models import Incident, Vehicle

class HandleIncidentSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Abaikan field yang tidak dikenal

    incident_id = fields.Integer(
        required=True,
        error_messages={
            "null": "ID insiden tidak boleh kosong.",
            "invalid": "ID insiden harus berupa angka."
        }
    )
    vehicles = fields.List(fields.Dict(
        fields={
            "vehicle_id": fields.Integer(required=True),
        }
    ), required=True, error_messages={"null": "Kendaraan tidak boleh kosong."})

    def __init__(self, db_session: Session, incident_id: int, *args, **kwargs):
        # Inisialisasi skema dengan sesi database dan ID insiden
        super().__init__(*args, **kwargs)
        self.db_session = db_session
        self.incident_id = incident_id
        # Ambil insiden berdasarkan incident_id
        self.current_incident = self.db_session.query(Incident).get(incident_id)
        if not self.current_incident:
            raise ValidationError({'incident_id': 'Laporan insiden tidak ditemukan'})

    @validates('incident_id')
    def validate_incident_id(self, value):
        # Validasi ID insiden jika diberikan
        if value is not None:  # Hanya validasi jika nilai diberikan
            incident = self.db_session.query(Incident).get(value)
            if not incident:
                raise ValidationError("Insiden dengan ID yang diberikan tidak ditemukan.")

    @validates('vehicles')
    def validate_vehicles(self, vehicles):
        # Validasi kendaraan dan driver untuk setiap kendaraan
        for vehicle in vehicles:
            vehicle_id = vehicle.get("vehicle_id")
            driver_id = vehicle.get("driver_id")
            
            # Validasi kendaraan berdasarkan vehicle_id
            existing_vehicle = self.db_session.query(Vehicle).get(vehicle_id)
            if not existing_vehicle:
                raise ValidationError(f"Kendaraan dengan ID {vehicle_id} tidak ditemukan.")
            