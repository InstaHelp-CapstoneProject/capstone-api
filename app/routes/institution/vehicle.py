from app.extensions import db
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify

from utils import auth
from app.models.models import Vehicle, User, Vehicle, Driver

# schemas
from app.schemas.vehicle.create_schema import CreateVehicleSchema
from app.schemas.vehicle.update_schema import UpdateVehicleSchema

vehicle_route = Blueprint('institutions/vehicles', __name__)

# Ambil Data
@vehicle_route.route('/', methods=['GET'])
@auth.login_required
def get_vehicles():
    # Dapatkan parameter kueri penelusuran
    search_name = request.args.get('name', None)

    # Bangun kuer
    query = db.session.query(
        Vehicle.id.label('vehicle_id'),
        Vehicle.is_ready,
        Vehicle.name,
        Vehicle.description,
        Vehicle.picture,
        Driver.id.label('driver_id'),
        User.name.label('driver_name'),
    ).join(Driver, Vehicle.driver_id == Driver.id) \
     .join(User, Driver.user_id == User.id)  # Gunakan alias di sini

    
    # Terapkan filter
    if search_name:
        query = query.filter(User.name.ilike(f'%{search_name}%'))  # Filter berdasarkan nama driver

    # Jalankan kueri
    vehicles = query.all()

    # Siapkan datanya
    vehicle_data = [
        {
            "id": vehicle.vehicle_id,
            "name": vehicle.name,
            "description": vehicle.description,
            "is_ready": vehicle.is_ready,
            "picture": vehicle.picture,
            "driver": {
                "id": vehicle.driver_id,
                "name": vehicle.driver_name
            }
        }
        for vehicle in vehicles
    ]

    return jsonify(
        status=True,
        message='Vehicles loaded successfully.',
        data=vehicle_data
    ), 200
# Akhir Ambil Data

# Tambah Kendaraan
@vehicle_route.route('/', methods=['POST'])
@auth.login_required
def add_vehicles():
     # Simpan data user ke database
    try:
        schema = CreateVehicleSchema(db_session=db.session)

        # Validasi permintaan data
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'status': False,
                'message': 'Validasi data gagal',
                'errors': err.messages
            }), 400
        
        new_vehicles = Vehicle(
            institution_id=data['institution_id'],
            driver_id=data['driver_id'],
            name=data['name'],
            picture=data['picture'],
            description=data['description'],
            is_ready=data['is_ready']
        )
        db.session.add(new_vehicles)

        # Simpan semua perubahan ke database
        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Kendaraan berhasil dibuat',
            'data': {
                'id': new_vehicles.id,
                'institution_id': new_vehicles.institution_id,
                'driver_id': new_vehicles.driver_id,
                'is_ready': new_vehicles.is_ready,
                'picture': new_vehicles.picture,
            }
        }), 201

    except Exception as e:
        # Rollback untuk semua jenis kesalahan
        db.session.rollback()
        
        # Tangani ValidationError secara spesifik
        if isinstance(e, ValidationError):
            return jsonify({
                'status': False,
                'message': 'Kesalahan validasi',
                'errors': e.messages
            }), 400
        
        # Tangani kesalahan umum
        return jsonify(
            status=False,
            message= f'Terjadi kesalahan: {str(e)}'
        ), 500
# Akhir Tambah Kendaraan

# Ubah Kendaraan 
@vehicle_route.route('/<int:vehicle_id>', methods=['PUT'])
@auth.login_required
def update_vehicle(vehicle_id):
    try:
        # Buat skema dengan data kendaraan saat ini
        schema = UpdateVehicleSchema(db_session=db.session, vehicle_id=vehicle_id)

        # Validasi permintaan data
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'status': False,
                'message': 'Validasi data gagal',
                'errors': err.messages
            }), 400

         # Get vehicle 
        vehicle = Vehicle.query.filter(vehicle_id).first()

        # Perbarui data kendaraan dengan fallback ke nilai yang ada
        vehicle.name = data.get('name', vehicle.name)
        vehicle.description = data.get('description', vehicle.description)
        vehicle.institution_id = data.get('institution_id', vehicle.institution_id)
        vehicle.driver_id = data.get('driver_id', vehicle.driver_id)
        vehicle.is_ready = data.get('is_ready', vehicle.is_ready)
        vehicle.picture = data.get('picture', vehicle.picture)

        # Lakukan perubahan
        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Kendaraan berhasil diperbarui',
            'data': {
                'vehicle': {
                    'id': vehicle.id,
                    'name': vehicle.name,
                    'description': vehicle.description,
                    'institution_id': vehicle.institution_id,
                    'driver_id': vehicle.driver_id,
                    'is_ready': vehicle.is_ready,
                    'picture': vehicle.picture
                }
            }
        }), 200

    except Exception as e:
        # Rollback untuk semua jenis kesalahan
        db.session.rollback()
        
        # Tangani ValidationError secara spesifik
        if isinstance(e, ValidationError):
            return jsonify({
                'status': False,
                'message': 'Kesalahan validasi',
                'errors': e.messages
            }), 400
        
        # Tangani kesalahan umum
        return jsonify(
            status=False,
            message= f'Terjadi kesalahan: {str(e)}'
        ), 500
# Akhir Ubah Kendaraan 

@vehicle_route.route('/<int:vehicle_id>', methods=['DELETE'])
@auth.login_required
def delete_driver(vehicle_id):
    try:
        # Query vehicle berdasarkan ID
        vehicle = Vehicle.query.filter_by(id=vehicle_id).first()
        
        if not vehicle:
            return jsonify({
                'status': False,
                'message': 'Kendaraan tidak ditemukan.'
            }), 404

        # Hapus data Vehicle
        db.session.delete(vehicle)

        # Commit transaksi
        db.session.commit()

        return jsonify(
            status= True,
            message='Kendaraan berhasil dihapus.'
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(
            status=False,
            message= f'Terjadi kesalahan: {str(e)}'
        ), 500
# Akhir Hapus Kendaraan