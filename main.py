from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from datetime import datetime, timedelta, date
import mysql.connector

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'tu_clave_secreta'  # Cambia esta clave a una más segura


CORS(app, origins=["http://localhost:3000"])

# Configuración de la base de datos MySQL
db_config = {
    'host': '34.71.110.169',
    'user': 'root',
    'password': 'Asmrg*1234',
    'database': 'gestoreventos'
}

# Función para obtener la conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Endpoint para crear un nuevo cliente
@app.route('/clientes', methods=['POST'])
def add_cliente():
    data = request.get_json()
    nombre = data['nombre']
    email = data['email']
    telefono = data.get('telefono', None)
    direccion = data.get('direccion', None)
    password_hash = data.get('password_hash')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Cliente WHERE email = %s", (email,))
    existing_cliente = cursor.fetchone()

    if existing_cliente:
        return jsonify({'message': 'Ya existe un cliente con este correo electrónico'}), 400

    cursor.execute(
        "INSERT INTO Cliente (nombre, email, password_hash, telefono, direccion) VALUES (%s, %s, %s, %s, %s)",
        (nombre, email, password_hash, telefono, direccion)
    )
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Cliente agregado exitosamente'}), 201

# Endpoint para obtener todos los clientes
@app.route('/clientes', methods=['GET'])
def get_clientes():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Cliente")
    clientes = cursor.fetchall()
    cursor.close()
    connection.close()

    return jsonify(clientes), 200

# Endpoint para obtener un cliente por ID
@app.route('/clientes/<int:id>', methods=['GET'])
def get_cliente(id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Cliente WHERE id_cliente = %s", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    connection.close()

    if cliente:
        return jsonify(cliente), 200
    else:
        return jsonify({'message': 'Cliente no encontrado'}), 404

# Endpoint para actualizar un cliente
@app.route('/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    data = request.get_json()
    nombre = data['nombre']
    email = data['email']
    telefono = data.get('telefono', None)
    direccion = data.get('direccion', None)

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE Cliente SET nombre = %s, email = %s, telefono = %s, direccion = %s WHERE id_cliente = %s",
        (nombre, email, telefono, direccion, id)
    )
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Cliente actualizado exitosamente'}), 200

# Endpoint para eliminar un cliente
@app.route('/clientes/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Cliente WHERE id_cliente = %s", (id,))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Cliente eliminado exitosamente'}), 200

# Endpoint para crear un nuevo proveedor
@app.route('/proveedores', methods=['POST'])
def add_proveedor():
    data = request.get_json()
    password = data.get('password_hash')

    if not password:
        return jsonify({'message': 'La contraseña es requerida'}), 400

    salt = bcrypt.gensalt()
    #hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    nombre = data['nombre']
    email = data['email']
    servicio = data['servicio']
    telefono = data.get('telefono', None)
    direccion = data.get('direccion', None)
    website = data.get('website', None)
    calificacion = data.get('calificacion', None)
    descripcion = data.get('descripcion', None)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Proveedor WHERE email = %s", (email,))
    existing_proveedor = cursor.fetchone()

    if existing_proveedor:
        return jsonify({'message': 'Ya existe un proveedor con este correo electrónico'}), 400

    cursor.execute(
        """INSERT INTO Proveedor 
           (nombre, servicio, telefono, direccion, email, password_hash, website, calificacion, descripcion) 
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (nombre, servicio, telefono, direccion, email, password, website, calificacion, descripcion)
    )
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Proveedor agregado exitosamente'}), 201

# Más endpoints según tu lógica inicial
# Endpoint para autenticar al proveedor
@app.route('/proveedores/login', methods=['POST'])
def login_proveedor():
    data = request.get_json()
    if 'email' not in data:
        return {'error': 'Falta el campo "email"'}, 400

    email = data['email']
    password = data['password']
    print(f"Email: {email}, Password: {password}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Proveedor WHERE email = %s", (email,))
    proveedor = cursor.fetchone()
    cursor.close()
    conn.close()

    if proveedor:
        password_hash_index = 6  # Ajusta el índice según tu tabla
        if password == proveedor[password_hash_index]:  # Cambiar según el hash real
            access_token = create_access_token(identity=proveedor[0])
            return jsonify({'message': 'Inicio de sesión exitoso', 'access_token': access_token}), 200
        else:
            return jsonify({'message': 'Credenciales incorrectas'}), 401
    else:
        return jsonify({'message': 'Proveedor no encontrado'}), 404

# Endpoint para obtener todos los proveedores
@app.route('/proveedores', methods=['GET'])
def get_proveedores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Proveedor")
    proveedores = cursor.fetchall()
    cursor.close()
    conn.close()

    proveedores_list = [
        {
            'id_proveedor': proveedor[0], 'nombre': proveedor[1], 'servicio': proveedor[2],
            'telefono': proveedor[3], 'direccion': proveedor[4], 'email': proveedor[5],
            'website': proveedor[7], 'calificacion': proveedor[8], 'descripcion': proveedor[9],
            'fecha_creacion': proveedor[10], 'activo': proveedor[11]
        }
        for proveedor in proveedores
    ]
    return jsonify(proveedores_list), 200

# Endpoint para actualizar un proveedor
@app.route('/proveedores/<int:id>', methods=['PUT'])
def update_proveedor(id):
    data = request.get_json()
    nombre = data['nombre']
    servicio = data['servicio']
    telefono = data.get('telefono', None)
    direccion = data.get('direccion', None)
    email = data['email']
    website = data.get('website', None)
    calificacion = data.get('calificacion', None)
    descripcion = data.get('descripcion', None)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE Proveedor SET nombre = %s, servicio = %s, telefono = %s, direccion = %s,
           email = %s, website = %s, calificacion = %s, descripcion = %s 
           WHERE id_proveedor = %s""",
        (nombre, servicio, telefono, direccion, email, website, calificacion, descripcion, id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Proveedor actualizado exitosamente'}), 200

# Endpoint para eliminar un proveedor
@app.route('/proveedores/<int:id>', methods=['DELETE'])
def delete_proveedor(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Proveedor WHERE id_proveedor = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Proveedor eliminado exitosamente'}), 200
# Endpoint para obtener notificaciones asociadas al proveedor que inició sesión
@app.route('/proveedores/notificaciones', methods=['GET'])
@jwt_required()  # Requiere autenticación con JWT
def get_notificaciones_proveedor():
    # Obtener el ID del proveedor desde el token JWT
    current_user = get_jwt_identity()

    try:
        # Conectar a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Ejecutar la consulta
        cursor.execute("""
            SELECT Notificacion.id_notificacion, Notificacion.mensaje, Notificacion.fecha
            FROM Notificacion
            WHERE Notificacion.id_usuario = %s AND Notificacion.tipo_usuario = 'Proveedor'
        """, (current_user,))
        
        notificaciones = cursor.fetchall()  # Las filas son devueltas como diccionarios
        # Transformar el resultado si es necesario
        notificaciones_list = [
            {
                'id_notificacion': notificacion['id_notificacion'],
                'mensaje': notificacion['mensaje'],
                'fecha': notificacion['fecha'].strftime('%Y-%m-%d %H:%M:%S') if notificacion['fecha'] else None
                
            }   
            for notificacion in notificaciones
        ]
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return jsonify({"message": "Error al obtener las notificaciones"}), 500

    finally:
        # Asegurar el cierre de recursos
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    # Retornar las notificaciones en formato JSON
    print("Notificaciones enviadas al cliente:", notificaciones_list)

    return jsonify({"notificaciones": notificaciones_list}), 200

# Endpoint para obtener eventos de un proveedor
@app.route('/proveedores/eventos', methods=['GET'])
@jwt_required()
def obtener_eventos_proveedor():
    proveedor_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Evento.*, Cliente.nombre, Cliente.telefono, Cliente.email
        FROM Evento
        INNER JOIN Evento_Proveedor ON Evento.id_evento = Evento_Proveedor.id_evento
        INNER JOIN Cliente ON Evento.id_cliente = Cliente.id_cliente
        WHERE Evento_Proveedor.id_proveedor = %s AND Evento_Proveedor.estado = 'Pendiente'
    """, (proveedor_id,))
    eventos = cursor.fetchall()

    if cursor.description is None:
        cursor.close()
        conn.close()
        return jsonify({"message": "Error al obtener los eventos."}), 500

    eventos_serializables = []
    for evento in eventos:
        evento_dict = {}
        for idx, value in enumerate(evento):
            column_name = cursor.description[idx][0]
            if isinstance(value, timedelta):
                evento_dict[column_name] = str(value)
            elif isinstance(value, (datetime, date)):
                evento_dict[column_name] = value.isoformat()
            else:
                evento_dict[column_name] = value
        eventos_serializables.append(evento_dict)

    cursor.close()
    conn.close()
    return jsonify({"eventos": eventos_serializables}), 200

# Endpoint para obtener eventos aceptados de un proveedor
@app.route('/proveedores/eventos-aceptados', methods=['GET'])
@jwt_required()
def obtener_eventos_aceptados_proveedor():
    proveedor_id = get_jwt_identity()
    print("ID proveedor en eventos-aceptados:", proveedor_id)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
       SELECT Evento.*, Cliente.nombre, Cliente.telefono, Cliente.email
        FROM Evento
        INNER JOIN Evento_Proveedor ON Evento.id_evento = Evento_Proveedor.id_evento
        INNER JOIN Cliente ON Evento.id_cliente = Cliente.id_cliente
        WHERE Evento_Proveedor.id_proveedor = %s AND Evento_Proveedor.estado = 'Rechazado'
    """, (proveedor_id,))
    eventos = cursor.fetchall()
    print("Eventos:", eventos)

    if cursor.description is None:
        cursor.close()
        conn.close()
        return jsonify({"message": "Error al obtener los eventos."}), 500

    eventos_serializables = []
    for evento in eventos:
        evento_dict = {}
        for idx, value in enumerate(evento):
            column_name = cursor.description[idx][0]
            if isinstance(value, timedelta):
                evento_dict[column_name] = str(value)
            elif isinstance(value, (datetime, date)):
                evento_dict[column_name] = value.isoformat()
            else:
                evento_dict[column_name] = value
        eventos_serializables.append(evento_dict)
    print("Eventos_serializables: ",eventos_serializables)

    cursor.close()
    conn.close()
    return jsonify({"eventos": eventos_serializables}), 200


@app.route('/eventos/<int:event_id>/estado', methods=['POST'])
@jwt_required()
def actualizar_estado_evento(event_id):
    # Obtener los datos del request
    data = request.json
    nuevo_estado = data.get('estado')  # "aceptado" o "rechazado"
    nuevo_estado = nuevo_estado.capitalize() 
    nuevo_estado = nuevo_estado.strip().capitalize()
    current_user = get_jwt_identity()
    print(f"Estado recibido (longitud {len(nuevo_estado)}): '{nuevo_estado}'")
    print("ID evento:", event_id)
    print("Proveedor actual:", current_user)
    if nuevo_estado not in ["Aceptado", "Rechazado"]:
        return jsonify({"message": "Se requiere el estado"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        print("Conexión exitosa")
        # Actualizar el estado del evento
        cursor.execute("""
            UPDATE Evento_Proveedor
            SET estado = %s
            WHERE id_evento = %s AND id_proveedor = %s
        """, (nuevo_estado, event_id, current_user))
        print("Estado actualizado")

        # Obtener los detalles del evento
        cursor.execute("SELECT id_cliente FROM Evento WHERE id_evento = %s", (event_id,))
        cliente_id = cursor.fetchone()
        if cliente_id:
            # Generar notificación para el cliente
            print("ID cliente:", cliente_id[0])
            cliente_id = cliente_id[0]  # Extraemos el id_cliente
            if nuevo_estado == "Aceptado":
                mensaje = f"El proveedor {current_user} aceptó el evento {event_id} del cliente {cliente_id}."
            else:
                mensaje = f"El proveedor {current_user} rechazó el evento {event_id} del cliente {cliente_id}."

            # Insertar la notificación en la base de datos
            cursor.execute("""
                INSERT INTO Notificacion (mensaje, id_usuario, tipo_usuario, fecha)
                VALUES (%s, %s, 'Cliente', NOW())
            """, (mensaje, cliente_id))

            print("Notificación creada para el cliente")

        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": "Error al procesar la solicitud"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    return jsonify({"message": "Estado actualizado y notificación creada"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Toma el puerto de entorno, usa 5000 como predeterminado
    app.run(host='0.0.0.0', port=port)
