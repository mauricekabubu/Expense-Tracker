from flask import Flask,render_template,redirect,request,flash,url_for,session
from flask_login import login_user,logout_user,current_user,login_manager,LoginManager,login_required
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime
from model import db,User,Expense,Category


app = Flask(__name__)

app.config["SECRET_KEY"] = "Mysecretkey"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def loader(user_id):
    return User.query.get(int(user_id))


#Setting up a home route
@app.route("/")
def home():
    return render_template("login.html")

#Setting up register route
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", category="danger")
            
        else:
            new_user = User(username=username,password=password)
            db.session.add(new_user)
            db.session.commit()
            
            flash("You have successfully created an new account!",category="success")
            return redirect(url_for("login"))
        
    return render_template("register.html")

#Setting up login route
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username = request.form.get("username")).first()
        
        if user and check_password_hash(user.password,request.form.get("password")):
            flash("Login successful!",category="success")
            login_user(user)
            
            return redirect(url_for("dashboard"))
        
        else:
            flash("Invalid username or password!",category="danger")
            
    return render_template("login.html")

#Setting up the dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    expenses = Expense.query.filter_by(user_id = current_user.id).all()
    category_totals = {}
    
    for exp in expenses:
        cat_name = exp.category.name if exp.category else "Uncategorised"
        category_totals[cat_name] = category_totals.get(cat_name,0) + exp.amount
        
    suggestions = []
    if category_totals:
        max_cat = max(category_totals, key=category_totals.get)
        max_amt = category_totals[max_cat]

        
        if max_amt >500:
            suggestions.append(f"You have spent kes{max_amt} on {max_cat} consider reducing it.")
            
        else:
            suggestions.append("Your spending is within healthy limits.")
            
    return render_template("dashboard.html",
                           username=current_user.username,expenses=expenses,
                           categories = list(category_totals.keys()),
                           totals = list(category_totals.values()),
                           suggestions = suggestions)
      
# SETTING UP THE CRUD ROUTES
# CRUD--> create, read, update and delete           
#Setting an add_user expenses route
@app.route("/add",methods=["GET","POST"])
@login_required
def add_expense():
    categories = Category.query.all()
    
    if request.method == "POST":
        title = request.form.get("title")
        amount = float(request.form.get("amount"))
        date = request.form.get("date")
        category_id = request.form.get("category_id")
        
        new_expense = Expense(
            title = title,
            amount = amount,
            date = date,
            user_id = current_user.id,
            category_id = category_id
        )
        db.session.add(new_expense)
        db.session.commit()
        flash("Expense added successfully.", category="success")
        
        return redirect(url_for("dashboard"))
    
    return render_template("add_expense.html", categories=categories)

#Setting up a category route
@app.route("/categories", methods=["GET", "POST"])
@login_required
def manage_categories():
    categories = Category.query.all()

    if request.method == "POST":
        name = request.form.get("category_name")
        if name:
            existing = Category.query.filter_by(name=name).first()
            if existing:
                flash("Category already exists!", category="warning")
            else:
                new_cat = Category(name=name)
                db.session.add(new_cat)
                db.session.commit()
                flash("Category added successfully!", category="success")
        else:
            flash("Category name cannot be empty.", category="danger")

        return redirect(url_for("manage_categories"))

    return render_template("category.html", categories=categories)

#Setting up edit category route
@app.route("/edit_category/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)

    if request.method == "POST":
        new_name = request.form.get("category_name")
        if new_name:
            category.name = new_name
            db.session.commit()
            flash("Category updated successfully!", category="success")
            return redirect(url_for("manage_categories"))
        else:
            flash("Category name cannot be empty.", category="danger")

    return render_template("edit category.html", category=category)


#Setting up delete category route
@app.route("/delete_category/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    if Expense.query.filter_by(category_id=category.id).first():
        flash("Cannot delete category in use by expenses.", category="danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully!", category="success")

    return redirect(url_for("manage_categories"))


#Setting edit expense route
@app.route("/edit/<int:id>",methods=["GET","POST"])
@login_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    categories = Expense.query.all()
    
    if expense.user_id != current_user.id:
        flash("Unauthorised access!", category="danger")
        
        return redirect(url_for("dash.board"))
    
    if request.method == "POST":
        expense.title = request.form.get("title")
        expense.amount = float(request.form.get("amount"))
        expense.date = request.form.get("date")
        expense.category_id = request.form.get("category_id")
        
        db.session.commit()
        flash("Expense updated successfully!", category="success")
        
        return redirect(url_for("dashboard"))
    
    return render_template("edit_expense.html",expense=expense,categories=categories)

#Setting a delete users expense data route
@app.route("/delete/<int:id>",methods=["GET","POST"])
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    
    if expense.user_id != current_user.id:
        flash("Unauthorised access!", category="danger")
        
        return redirect(url_for("dashboard"))
    
    db.session.delete(expense)
    db.session.commit()
    
    flash("Expense deleted successfully.", category="success")
    
    return redirect(url_for("dashboard"))
    
    
#Setting logout route
@app.route("/logout")
def logout():
    session.pop("username",None)
    flash("You have been logout successfully",category="success")
    
    logout_user()
    
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)