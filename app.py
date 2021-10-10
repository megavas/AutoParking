import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import current_user, login_user, login_required, LoginManager, logout_user
from flask_session import Session
from config_lang import ConfigLang

login_manager = LoginManager()

app = Flask(__name__)

#'postgresql://username:password@host:port/database'

uri = 'postgresql://zgnojbpnkhoqmx:5d8d7241e51758b68ce3aa6c365d746d4ea3b8a711a2b5d31c33100ef7a6705a@ec2-44-196-146-152.compute-1.amazonaws.com:5432/d26fib3rqoq9p1' # produccion

from config import config
uri = config() # megavas

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(32)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager.init_app(app)
login_manager.login_view = "index"

from models.rol import Rol
from models.documento import Documento
from models.tipovehiculo import TipoVehiculo
from models.tarifa import Tarifa
from models.usuario import Usuario
from models.parqueadero import Parqueadero
from models.vehiculo import Vehiculo
from models.factura import Factura

langIni = 'lang_ESP.ini'

@app.route("/", methods=["GET", "POST"])
def index():
    if(request.method == "POST"):
        usuario = request.form["user"]
        password = request.form["pass"]
        
        validate = Usuario.login(usuario, password)
        print(validate[1])
        if validate[0]:
            login_user(validate[1])
            return redirect(url_for("users"))
    
    lang = ConfigLang(langIni, 'LOGIN')
    return render_template('index.html', lang=lang)

@app.route("/ventas", methods=["GET", "POST"])
def ventas():
    lang = ConfigLang(langIni, 'LOGIN')
    return render_template('ventas.html', lang=lang)

@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if current_user.id_r == 1:
        alerta = ["", '']
        tipo_doc = Documento.get_all()
        usuarios = Usuario.get_full()
        edit = 0
        
        if(request.method == "POST"):
            t_doc = request.form["t_doc"]
            documento = request.form["documento"]
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            telefono = request.form["tel"]
            correo = request.form["email"]
            usuario = request.form["user"]
            password = request.form["pass"]
            id_r = request.form["rol"]
            
            user = Usuario(t_doc, documento, nombre, apellido, telefono, correo, usuario, password, id_r)
            if Usuario.if_noexist(documento, id_r):
                user.create()
                
                alerta[0] = "success"
                alerta[1] = "El usuario se ha creado."
            else:
                edit = int(request.form["edit"])
                if edit > 0:
                    user.update_user(edit, user)
                    alerta[0] = "warning"
                    alerta[1] = "El usuario se ha modificado."
                else:
                    print("no")
                    alerta[0] = "danger"
                    alerta[1] = "El documento ya está asociado a ese tipo de usuario."
            
        lang = ConfigLang(langIni, 'LOGIN')
        return render_template('usuarios.html', alerta=alerta, tipo_doc=tipo_doc, usuarios=usuarios, lang=lang, edit=0)
        
    else:
        return redirect(url_for('ventas'))

@app.route("/ajaxfile",methods=["POST","GET"])
def ajaxfile():
    tipo_doc = Documento.get_all()
    if request.method == "GET":
        edit = request.args.get('userid')
        if edit == None:
            return jsonify({'htmlresponse': render_template('usuarios_response.html', tipo_doc=tipo_doc, edit=0)})
        else:
            user = Usuario.get_user(edit)
            return jsonify({'htmlresponse': render_template('usuarios_response.html', tipo_doc=tipo_doc, edit=int(edit), who=user)})
    
@app.route("/tarifas")
def tarifas():
    tarifa=Tarifa.get_full()
    
    return render_template('tarifas.html',tarifa=tarifa)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)