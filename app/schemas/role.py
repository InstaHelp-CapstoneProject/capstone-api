from marshmallow import Schema, fields, validate

class CreateRoleSchema(Schema):
    name = fields.String(
        required=True, 
        validate=[validate.Length(min=5, error="Nama role harus minimal 3 karakter.")],
        error_messages={
            "required": "Nama role wajib diisi.",
            "null": "Nama role tidak boleh kosong."
        }
    )

class UpdateRoleSchema(Schema):
    name = fields.String(
        required=False, 
        validate=[validate.Length(min=5, error="Nama role harus minimal 3 karakter.")],
        error_messages={
            "null": "Nama role tidak boleh kosong."
        }
    )