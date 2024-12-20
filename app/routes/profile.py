from flask_jwt_extended import get_jwt_identity
from flask import Blueprint, request, jsonify
from app.extensions import db
from marshmallow import ValidationError

from utils import auth
from app.models.models import User

from app.schemas.profile_schema import ResidentProfileSchema, DriverProfileSchema, InstitutionProfileSchema, AdministrationProfileSchema

user_route = Blueprint('profiles', __name__)

@user_route.route('/', methods=['GET'])
@auth.login_required
def profile_me():
    # Ambil user dari token otentikasi
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "Profil tidak ditemukan"}), 404

    # Ambil role user
    roles = [role.name for role in user.roles]

    # Respons berdasarkan role
    if "resident" in roles:
        resident = user.resident
        if not resident:
            return jsonify({"error": "Resident data tidak ditemukan"}), 404

        response = {
            "id": user.id,
            "username": user.username,
            "address": user.address,
            "name": user.name,
            "email": user.email,
            "nik": resident.nik,
            "phone_number": resident.phone_number,
            "date_of_birth": resident.date_of_birth.strftime('%Y-%m-%d'),
            "place_of_birth": resident.place_of_birth,
            "gender": resident.gender.value,
        }

    elif "driver" in roles:
        driver = user.driver
        if not driver:
            return jsonify({"error": "Driver data tidak ditemukan"}), 404

        response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "phone_number": driver.phone_number,
            "institution_id": driver.institution_id,
        }

    elif "institution" in roles:
        institution = user.institution
        if not institution:
            return jsonify({"error": "Institution data tidak ditemukan"}), 404

        # print(institution.id)
        response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "description": institution.description,
            "location": {
                "latitude": institution.latitude,
                "longitude": institution.longitude,
            },
        }

    elif "administration" in roles:
        response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "address": user.address,
            "created_at": user.created_at,
        }

    else:
       return jsonify({"error": "Pengguna tidak ditemukan"}), 404

    return jsonify(response)

@user_route.route('/update', methods=['PUT'])
@auth.login_required
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "Profil tidak ditemukan"}), 404
    
    # Get user's role
    user_role = user.roles[0].name if user.roles else None
    
    try:
        # Pilih skema yang sesuai berdasarkan peran pengguna
        if user_role == 'resident':
            # Validasi permintaan data
            schema = ResidentProfileSchema(db_session=db.session, user_id=user_id)

            try:
                data = schema.load(request.json)
            except ValidationError as err:
                return jsonify({
                    'status': False,
                    'message': 'Validasi data gagal',
                    'errors': err.messages
                }), 400
            
            # Perbarui data spesifik penduduk hanya jika tersedia
            resident = user.resident
            if not resident:
                return jsonify({"error": "Masyarakat data tidak ditemukan"}), 404
            
            # Mulailah transaksi
            db.session.begin_nested()

            # Ubah user data
            user.name = data.get('name', user.name)
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.address = data.get('address', user.address)

            # Ubah data Masyarakat
            resident.nik = data.get('nik', resident.nik)
            resident.phone_number = data.get('phone_number', resident.phone_number)
            resident.date_of_birth = data.get('date_of_birth', resident.date_of_birth)
            resident.place_of_birth = data.get('place_of_birth', resident.place_of_birth)
            resident.gender = data.get('gender', resident.gender)
            
            db.session.commit()

            return jsonify({
                'status': True,
                'message': 'Profil berhasil diperbarui',
                "data" : {
                    'user': user.as_dict(),
                    "resident": {  
                        "nik": resident.nik,
                        "phone_number": resident.phone_number,
                        "date_of_birth": resident.date_of_birth.strftime('%Y-%m-%d'),
                        "place_of_birth": resident.place_of_birth,
                        "gender": resident.gender.value
                    }
                }
            }), 200

        elif user_role == 'driver':
            # Validasi permintaan data
            schema = DriverProfileSchema(db_session=db.session, user_id=user_id)
            try:
                data = schema.load(request.json)
            except ValidationError as err:
                return jsonify({
                    'status': False,
                    'message': 'Validasi data gagal',
                    'errors': err.messages
                }), 400
            
            driver = user.driver
            if not driver:
                return jsonify({"error": "Driver data tidak ditemukan"}), 404
            
            # Mulailah transaksi
            db.session.begin_nested()
            
            # Ubah user data
            user.name = data.get('name', user.name)
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.address = data.get('address', user.address)

            # Ubah data Pengemudi
            driver.phone_number = data.get('phone_number', driver.phone_number)
            driver.institution_id = data.get('institution_id', driver.institution_id)
            
            db.session.commit()

            return jsonify({
                'status': True,
                'message': 'Profil berhasil diperbarui',
                "data" : {
                    'user': user.as_dict(),
                    "driver": {  
                        "phone_number": driver.phone_number,
                        "institution_id": driver.institution_id
                    }
                }
            }), 200

        elif user_role == 'institution':
            # Validasi permintaan data
            schema = InstitutionProfileSchema(db_session=db.session, user_id=user_id)
            
            try:
                data = schema.load(request.json)
            except ValidationError as err:
                return jsonify({
                    'status': False,
                    'message': 'Validasi data gagal',
                    'errors': err.messages
                }), 400
            
            institution = user.institution
            if not institution:
                return jsonify({"error": "Institution data tidak ditemukan"}), 404
            
            # Begin transaction
            db.session.begin_nested()

            # Ubah user data
            user.name = data.get('name', user.name)
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.address = data.get('address', user.address)
            
            # Ubah data Instansi
            institution.description = data.get('description', institution.description)
            institution.latitude = data.get('latitude', institution.latitude)
            institution.longitude = data.get('longitude', institution.longitude)
            
            db.session.commit()
            return jsonify({
                'status': True,
                'message': 'Profil berhasil diperbarui',
                "data" : {
                    'user': user.as_dict(),
                    "driver": {  
                         "description": institution.description,
                        "location": {
                            "latitude": institution.latitude,
                            "longitude": institution.longitude,
                        },
                    }
                }
            }), 200

        elif user_role == 'administration':
            schema = AdministrationProfileSchema(db_session=db.session, user_id=user_id)
            try:
                data = schema.load(request.json)
            except ValidationError as err:
                return jsonify({
                    'status': False,
                    'message': 'Validasi data gagal',
                    'errors': err.messages
                }), 400

            db.session.commit()

            # Ubah user data
            user.name = data.get('name', user.name)
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.address = data.get('address', user.address)

            return jsonify({
                'status': True,
                'message': 'Profil berhasil diperbarui',
                "data" : {
                    'user': user.as_dict()
                }
            }), 200
        else:
            return jsonify({'status': False, 'message': 'Role pengguna tidak valid'}), 400

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
            
        return jsonify(
            status=False,
            message= f'Terjadi kesalahan: {str(e)}'
        ), 500
