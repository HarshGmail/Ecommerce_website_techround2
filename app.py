from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ecommerce_database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class user_Database(db.Model):
    username = db.Column(db.String(30), primary_key = True)
    name = db.Column(db.String(30))
    password = db.Column(db.String(30))
    usertype = db.Column(db.String(6))

class products_Database(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30))
    name = db.Column(db.String(30))
    price = db.Column(db.Float)

class orders_Database(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    username_buyer = db.Column(db.String(30))
    username_seller = db.Column(db.String(30))
    name = db.Column(db.String(30))
    price = db.Column(db.Float)

class cart_Database(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    username_buyer = db.Column(db.String(30))
    username_seller = db.Column(db.String(30))
    name = db.Column(db.String(30))
    price = db.Column(db.Float)

class wishlist_Database(db.Model):
    sno = db.Column(db.Integer, primary_key = True)
    username_buyer = db.Column(db.String(30))
    username_seller = db.Column(db.String(30))
    name = db.Column(db.String(30))
    price = db.Column(db.Float)

db.create_all()

@app.route("/", methods = ["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        u_data = user_Database.query.all()
        for row in u_data:
            if str(row.username) == str(username) and str(row.password) == str(password):
                if str(row.usertype) == "seller":
                    return redirect(url_for("seller_home_page", username = username))
                else:
                    return redirect(url_for("buyer_home_page", username = username))
            elif (str(row.username) == str(username) and str(row.password) != str(password)) or (str(row.username) != str(username) and str(row.password) == str(password)):
                render_template("login.html", error = f"there is a mistake in username or password")
        else:
            return render_template("login.html", error = f"{username} doesn't exist, sign up now!!")
    return render_template("login.html")

@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method=="POST":
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        usertype = request.form['user_type']
        u_data = user_Database.query.all()
        for row in u_data:
            if str(row.username) == str(username):
                return render_template("signup.html", error = f"{username} already exists choose something else")
        else:
            row = user_Database(username = username, name = name, password = password, usertype = usertype)
            db.session.add(row)
            db.session.commit()
            if str(usertype) == "Seller":
                return redirect(url_for("seller_home_page", username = username))
            else:
                return redirect(url_for("buyer_home_page", username = username))
            
    return render_template("signup.html")

@app.route("/seller_home_page/<username>", methods = ["POST", "GET"])
def seller_home_page(username):
    p_data = products_Database.query.all()
    return render_template("seller_home_page.html", username = username, p_data = p_data)

@app.route("/buyer_home_page/<username>", methods = ["POST", "GET"])
def buyer_home_page(username):
    p_data = products_Database.query.all()
    return render_template("buyer_home_page.html", username = username, p_data = p_data)

@app.route("/add_product/<username>", methods = ["POST", "GET"])
def add_products(username):
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        p_data = products_Database.query.all()
        sno = 0
        for row in p_data:
            sno = int(row.sno)
        sno+=1
        row = products_Database(sno = sno, username = username[1:-1], name = name, price = price)
        db.session.add(row)
        db.session.commit()
        return redirect(url_for("seller_home_page", username = username))
    return render_template("add_product.html", username = username)

@app.route("/modify_product/<username>/<sno>/<name>", methods = ["POST", "GET"])
def modify_product(username, sno, name):
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        row = products_Database.query.filter_by(sno = sno).first()
        row.sno = sno
        row.username = username[1:-1]
        row.name = name
        row.price = price
        db.session.add(row)
        db.session.commit()
        return redirect(url_for("seller_home_page", username = username))
    return render_template("modify_product.html", username = username, name= name, sno = sno)

@app.route("/delete_product/<username>/<sno>/<type>", methods=["POST", "GET"])
def delete_product(username, sno, type):
    row = user_Database.query.filter_by(username=username).first()
    if str(row.usertype) == "seller":
        r = products_Database.query.filter_by(sno=sno).first()
        if r:
            db.session.delete(r)
            db.session.commit()
    else:
        if type == 'cart':
            r = cart_Database.query.filter_by(sno=sno).first()
            if r:
                db.session.delete(r)
                db.session.commit()
        else:
            r = wishlist_Database.query.filter_by(sno=sno).first()
            if r:
                db.session.delete(r)
                db.session.commit()

    if str(row.usertype) == "seller":
        return redirect(url_for("seller_home_page", username=username))
    else:
        return redirect(url_for("buyer_home_page", username=username))

    

@app.route("/add_to_cart/<username>/<sno>/<sellername>/<name>/<price>")
def add_to_cart(username, sno, sellername, name, price):
    r = cart_Database.query.all()
    sno = 0
    for k in r:
        sno = int(k.sno)
    sno += 1
    row = cart_Database(sno=sno, username_buyer=username, username_seller=sellername, name=name, price=price)
    db.session.add(row)
    db.session.commit()
    return redirect(url_for("cart", username=username))

@app.route("/cart/<username>")
def cart(username):
    data = cart_Database.query.filter_by(username_buyer=username).all()
    return render_template("cart.html", username=username, data=data)
    
@app.route("/add_to_wishlist/<username>/<sno>/<sellername>/<name>/<price>")
def add_to_wishlist(username, sno, sellername, name, price):
    r = wishlist_Database.query.all()
    sno = 0
    for k in r:
        sno = int(k.sno)
    sno += 1
    row = wishlist_Database(sno=sno, username_buyer=username, username_seller=sellername, name=name, price=price)
    db.session.add(row)
    db.session.commit()
    return redirect(url_for("wishlist", username=username))

@app.route("/wishlist/<username>")
def wishlist(username):
    data = wishlist_Database.query.filter_by(username_buyer=username).all()
    return render_template("wishlist.html", username=username, data=data)
@app.route("/buy/<username>/<sno>/<name>")

@app.route("/buy/<username>/<sno>/<name>/<sellername>/<price>")
def buy(username, sno, name, sellername, price):
    data = orders_Database().query.all()
    sn = 0
    for k in data:
        sn = int(k.sno)
    sn += 1
    row = orders_Database(sno=sn, username_buyer=username, username_seller=sellername, name=name, price=price)
    db.session.add(row)
    db.session.commit()
    data = cart_Database().query.filter_by(sno=sno).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("orders", username=username))


@app.route("/orders/<username>")
def orders(username):
    r = user_Database.query.filter_by(username=username).first()
    if r.usertype == 'seller':
        data = orders_Database.query.filter_by(username_seller=username)
    else:
        data = orders_Database.query.filter_by(username_buyer=username)

    return render_template("orders.html", username=username, data=data)



if __name__ == "__main__":
    app.run(debug = True)