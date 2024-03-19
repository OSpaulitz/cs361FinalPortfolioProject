from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Recipe  
from . import db
import json
import zmq

debug = 1

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


views = Blueprint('views', __name__)



@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


#  database and microservice implementations seen below
@views.route('/recipe', methods=['GET', 'POST'])
def recipe():
    if request.method == "POST":
        recipe_name = request.form['name']
        recipe_category = request.form['category']
        recipe_ingredients = request.form['ingredients']
        recipe_instructions = request.form['instructions']
        new_recipe = Recipe(name=recipe_name, category=recipe_category, ingredients=recipe_ingredients, instructions=recipe_instructions)#, user_id=current_user.id)

        #push to database
        try:
            db.session.add(new_recipe)
            db.session.commit()

            # microservice implementation
            debug == 1

            if debug == 1:
                print("sending admin message command")
            socket.send_string(f"TYPE: admin; CONTACT: paulitzj@oregonstate.edu; RECIPE NAME: {recipe_name}; RECIPE: ingredients: \
            {recipe_ingredients} instructions: {recipe_instructions}; USER: {current_user.email}")  
            message = socket.recv()
            if debug == 1:
                print("received response "+str(message))

            if debug == 1:
                print("sending user message command")
            socket.send_string(f"TYPE: user; CONTACT: {current_user.email}; RECIPE NAME: {recipe_name}")  
            message = socket.recv()
            if debug == 1:
                print("received response "+str(message))

            # end microservice
            return redirect('/recipe')
        

        
        except Exception as e:
            db.session.rollback()
            print(f"Error adding recipe:{str(e)}")
            return "There was an error adding your recipe"

    else:
        recipe = Recipe.query.order_by(Recipe.name.desc())
        return render_template("recipe.html", user=current_user, recipe=recipe)
    
  

