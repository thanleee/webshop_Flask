from flask import render_template, request, session, redirect, url_for

from shop import app, db
@app.route('/')
def home():
    return "Home page of myshop"