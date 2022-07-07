"""
This is a set of methods that will be used to implement the user's utilites for
Digital Notes.
"""

import flask as fk
import pymongo as pm
import re
from datetime import date

# User's bp
user = fk.Blueprint("user", __name__, static_folder="static", template_folder="templates")


# Initialize client
client = pm.MongoClient("mongodb://mongodb:27017/")
db = client["DigitalNotes"]
notesDb = db["notes"]
usersDb = db["users"]


# User's home page which also shows all the notes.
@user.route("/")
@user.route("/userShowNotes", methods=["GET","POST"])
def userHPage():
    if fk.request.method == "GET":
        all_notes = notesDb.find({"username":fk.session["username"]})
        return fk.render_template("userShowNotes.html", usName = fk.session["username"], notes = all_notes)
    else:
        all_notes = notesDb.find({"username":fk.session["username"]})
        if fk.request.form["submit_button"] == "Newer":
            sorted_notes = sorted(all_notes, key=lambda x: x["crDate"], reverse=True)
        elif fk.request.form["submit_button"] == "Older":
            sorted_notes = sorted(all_notes, key=lambda x: x["crDate"], reverse=False)
        return fk.render_template("userShowNotes.html", usName = fk.session["username"], notes = sorted_notes)

# Create note.
@user.route("/")
@user.route("/createNote", methods=["GET","POST"])
def createNote():
    if fk.request.method == "GET":
        return fk.render_template("createNote.html")
    else:
        #request values
        title = fk.request.form["title"]
        content = fk.request.form["content"]
        crDate = date.today().strftime("%d/%m/%Y")
        kwords = fk.request.form["kwords"]

        if notesDb.find_one({"$and":[ {"username":fk.session["username"]}, {"title": title} ]}):
            fk.flash(f"You alredy have a note with the title: { title }")
            return fk.redirect(fk.url_for("user.createNote"))
        else :
            newNote = {"username":fk.session["username"], "title": title, "content": content, "crDate": crDate, "kwords": kwords}
            notesDb.insert_one(newNote)
            fk.flash("Note successfully created!")
            return fk.redirect(fk.url_for("user.userHPage"))


# Search via Title
@user.route("/search")
@user.route("/searchViaTitle", methods=["GET", "POST"])
def searchViaTitle():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaTitle.html")
    else:
        title = fk.request.form["title"]
        # Make a variable to catch all reuslts similar to title in case of wrong spelling.
        like_title = re.compile(f"[{title}]")
        results = notesDb.find({"$and":[ {"username":fk.session["username"]}, {"title": like_title} ]})
        if results is None:
            fk.flash("No results found.")
            return fk.redirect(fk.url_for("user.searchViaTitle"))
        else:
            return fk.render_template("userSearchResultsT.html", notes=results)


# Search via Key-words
@user.route("/search")
@user.route("/searchViaKwords", methods=["GET","POST"])
def searchViaKwords():
    if fk.request.method == "GET":
        return fk.render_template("userSearchViaKwords.html")
    else:
        kWord = fk.request.form["kwords"]
        like_kword = re.compile(f",*{kWord}*,")
        results = notesDb.find({"$and":[ {"username":fk.session["username"]}, {"kwords": like_kword} ]})
        if results is None:
            fk.flash("No results found.")
            return fk.redirect(fk.url_for("user.searchViaKwords"))
        else:
            return fk.render_template("userSearchResultsKW.html", notes=results)


# Edit note.
@user.route("/")
@user.route("/editNote", methods=["GET", "POST"])
def editNote():
    if fk.request.method == "GET":
        # Show user all notes so he can choose.
        all_notes = notesDb.find({"username":fk.session["username"]})
        return fk.render_template("editNote.html",notes=all_notes)
    else:
        old_title = fk.request.form["title"]
        old_note = notesDb.find_one({"$and":[ {"username":fk.session["username"]}, {"title": old_title} ]})
        if old_note is None:
            fk.flash("There is no note with such title.")
            return fk.redirect(fk.url_for("user.editNote"))
        else:
            new_title = fk.request.form["new_title"]
            new_content = fk.request.form["new_content"]
            new_kwords = fk.request.form["new_kwords"]
            notesDb.update_one({"_id": old_note["_id"]}, {"$set": {"title":new_title, "content":new_content, "kwords":new_kwords}})
            fk.flash("Note successfully updated!")
            return fk.redirect(fk.url_for("user.userHPage"))


# Delete note.
@user.route("/")
@user.route("/deleteNote", methods=["GET","POST"])
def deleteNote():
    if fk.request.method == "GET":
        # Show user all notes so he can choose.
        all_notes = notesDb.find({"username":fk.session["username"]})
        return fk.render_template("deleteNote.html", notes=all_notes)
    else:
        title = fk.request.form["title"]
        dead_note = notesDb.find_one({"$and":[ {"username":fk.session["username"]}, {"title":title} ]})
        if dead_note is None:
            fk.flash("There is no note with such title.")
            return fk.redirect(fk.url_for("user.deleteNote"))
        else:
            notesDb.delete_one({"$and":[ {"username":fk.session["username"]}, {"title": title} ]})
            fk.flash("Note successfully deleted!")
            return fk.redirect(fk.url_for("user.userHPage"))


# Delete account.
@user.route("/")
@user.route("/deleteAccount", methods=["GET","POST"])
def deleteAccount():
    if fk.request.method == "GET":
        return fk.render_template("deleteAccount.html")
    else:
        username = fk.request.form["username"]
        if username == fk.session["username"]:
            usersDb.delete_one({"username": username})
            notesDb.delete_many({"username": username})
            fk.flash("Account successfully deleted!")
            return fk.redirect(fk.url_for("auth.signUp"))
        else:
            fk.flash("Invalid username")
            return fk.redirect(fk.url_for("user.deleteAccount"))
