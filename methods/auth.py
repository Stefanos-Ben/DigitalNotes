import flask as fk
import pymongo as pm

#Authentication bp.
auth = fk.Blueprint("auth", __name__, static_folder="static", template_folder="templates")

# Initialize client
client = pm.MongoClient("mongodb://mongodb:27017/")
db = client["DigitalNotes"]
notesDb = db["notes"]
usersDb = db["users"]


#Sign Up.
@auth.route("/signUp", methods=["GET", "POST"])
def signUp():
    if fk.request.method == "GET":
        return fk.render_template("signUp.html")
    else:
        username = fk.request.form["username"]
        email = fk.request.form["email"]
        password = fk.request.form["password"]
        fullname = fk.request.form["fullname"]
        # Check if email or username exists.
        exists_mail = usersDb.find_one({"email":email})
        exists_name = usersDb.find_one({"username":username})
        if (exists_mail is None) and (exists_name is None):
            new_user = {"username": username, "password": password, "email": email, "fullname": fullname, "property": "user"}
            usersDb.insert_one(new_user)
            return fk.redirect(fk.url_for("auth.signIn"))
        elif exists_name is None:
            fk.flash("This email is already being used!")
            return fk.redirect(fk.url_for("auth.signUp"))
        else:
            fk.flash("This username is already being used!")
            return fk.redirect(fk.url_for("auth.signUp"))


# Sign In.
@auth.route("/")
@auth.route("/signIn", methods=["GET","POST"])
def signIn():
    if fk.request.method == "GET":
        return fk.render_template("signIn.html")
    else:
        name = fk.request.form["name"]
        password = fk.request.form["password"]
        user = usersDb.find_one({"$or":[ {"email":name}, {"username":name} ]})
        if user is None:
            fk.flash("Invalid e-mail or username.")
            return fk.redirect(fk.url_for("auth.signIn"))
        elif user["password"] == password:
            # Assign session variables
            fk.session["email"] = user["email"]
            fk.session["username"] = user["username"]
            # Log In according to property
            if user["property"] == "admin":
                fk.flash(f"Successfully logged in as { name }")
                if password == "otpword":
                    return fk.redirect(fk.url_for("auth.changePass"))
                else:
                    return fk.redirect(fk.url_for("admin.adminHP"))
            else:
                fk.flash(f"Successfully logged in as { name }")
                return fk.redirect(fk.url_for("user.userHPage"))
        else:
            fk.flash("Invalid password")
            return fk.redirect(fk.url_for("auth.signIn"))


# Sign out.
@auth.route("/signOut")
def signOut():
    fk.session.pop("email", None)
    fk.session.pop("username", None)
    return fk.redirect(fk.url_for("auth.signIn"))


# Change password.
@auth.route("/")
@auth.route("/changePass", methods=["GET","POST"])
def changePass():
    if fk.request.method == "GET":
        return fk.render_template("changePass.html")
    else:
        new_pass = fk.request.form["new_pass"]
        email = fk.session["email"]
        if new_pass == "otpword":
            fk.flash("This password can't be used by an admin.Please try a diffferent password.")
            return fk.redirect(fk.url_for(auth.changePass))
        else:
            user = usersDb.find_one({"email":email})
            usersDb.update_one({"_id":user["_id"]}, {"$set":{"password":new_pass}})
            fk.flash("Successfully updated password")
            return fk.redirect(fk.url_for("admin.adminHP"))
