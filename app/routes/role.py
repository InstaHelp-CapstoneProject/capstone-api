import os
from app.extensions import db
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify

from utils import auth
from app.models.models import Role

# schemas
from app.schemas.role import CreateRoleSchema, UpdateRoleSchema

role_route = Blueprint('roles', __name__)

# Ambil Data
@role_route.route('/', methods=['GET'])
@auth.login_required
def get_vehicles():
    # Dapatkan parameter kueri penelusuran
    search_name = request.args.get('name', None)

    # Bangun kueri
    query = db.session.query(
        Role.id.label('role_id'),
        Role.name,
        Role.created_at
    ) 
    
    # Terapkan filter
    if search_name:
        query = query.filter(Role.name.ilike(f'%{search_name}%'))  # Filter berdasarkan nama driver

    # Jalankan kueri
    roles = query.all()

    # Siapkan datanya
    role_data = [
        {
            "id": role.role_id,
            "name": role.name,
            "created_at": role.created_at,
        }
        for role in roles
    ]

    return jsonify(
        status=True,
        message='Role berhasil dimuat.',
        data=role_data
    ), 200
# Akhir Ambil Data

# Tambah Role
@role_route.route('/', methods=['POST'])
@auth.login_required
def add_roles():
     # Simpan data user ke database
    try:
        schema = CreateRoleSchema()

        # Validasi permintaan data
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return jsonify({
                'status': False,
                'message': 'Validasi data gagal',
                'errors': err.messages
            }), 400
        
        new_roles = Role(
            name=data['name'],
        )
        db.session.add(new_roles)

        # Simpan semua perubahan ke database
        db.session.commit()

        return jsonify({
            'status': True,
            'message': 'Role berhasil dibuat',
            'data': {
                'id': new_roles.id,
                'name': new_roles.name,
                'created_at': new_roles.created_at,
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
# Akhir Tambah Role

@role_route.route('/<int:role_id>', methods=['DELETE'])
@auth.login_required
def delete_driver(role_id):
    try:
        # Kueri role berdasarkan ID
        role = Role.query.filter_by(id=role_id).first()
        
        if not role:
            return jsonify({
                'status': False,
                'message': 'Role tidak ditemukan.'
            }), 404

        # Hapus data Role
        db.session.delete(role)

        # Commit transaksi
        db.session.commit()

        return jsonify(
            status= True,
            message='Role berhasil dihapus.'
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify(
            status=False,
            message= f'Terjadi kesalahan: {str(e)}'
        ), 500
# Akhir Hapus Role