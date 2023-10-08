#import necessary libraries
import flask
from flask import Flask, render_template, request, url_for,redirect
import requests
#import json in order to read the text returned from the api
#https://www.nylas.com/blog/use-python-requests-module-rest-apis/ was used to determine that json was needed in order to query for data from the api
#https://www.w3schools.com/python/python_json.asp was used to better understand what json does and how it is implemented
import json

#configure application
    #in order for application to run the following must be run in the terminal:
        #export FLASK_APP=main
        #used https://fixexception.com/flask/could-not-locate-a-flask-application-you-did-not-provide-the-flask-app-environment-variable-and-a-wsgi-py-or-app-py-module-was-not-found-in-the-current-directory/ to figure this out as server was not running before
app = Flask(__name__)
#make empty dictionary for json
    #json uses a dictionary as seen on https://www.w3schools.com/python/python_json.asp
dict = {}
#make a get request for the information from the api using requests.get()
    #https://docs.python-requests.org/en/latest/ was used to understand how to get information from api
r = requests.get('https://pokeapi.co/api/v2/pokemon?limit=890')
#take the requests (which are given in json format) and make a list of the json content
#https://www.geeksforgeeks.org/response-json-python-requests/ was used to better understand json requests
list=r.json()
#iterate through the list in order to otain information about each pokemon
    #iterate through the 'results' of the json content within the list created
for i in list['results']:
    #obtain the url for each pokemon which will redirect to more json content about the specific pokemon selected
    req = requests.get(i['url']).json()
    #obtain a number to use for finding the image of the pokemon
    #the image number is in a three digit format so if it is the first pokemon the number will be 001
        #in order to get the desired number to input into the url, use str.zfill() which takes a str(object) which in this case will be the id number of the pokemon, and then it fills in 0s in front of the number until a specified length is met
        #so using str(id).zfill(3) will take the id and put 0s in front of it until the strlen is 3
        #ex: if id = 1 then nr = 001, if id = 28 then nr = 028 and so on...
        #req['id'] allows me to take the id number associated within the request json format so id : ___ and it will return ___ aka the number
        #https://www.w3schools.com/python/ref_string_zfill.asp and https://www.kite.com/python/answers/how-to-add-leading-zeros-to-a-number-in-python were used to understand str.zfill
    nr = str(req['id']).zfill(3)
    #obtain the name of the pokemon using the same method for obtaining the nr except this time zfill is not needed
    name = req['name']
    #obtain the png image from the following link using the nr obtained earlier
    png = f'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{nr}.png'
    #assign the png to the pokemon
    dict[name] = png

#make an app.route and set values for parameters to empty
    #this is done so that one part of the screen will have the list of pokemon whereas the other part of the screen will be blank until a pokemon is selected or a "focus" is set
@app.route('/', defaults={'focus': '','name': '','img': '','ability': '','type': ''})
#make the app.route have the following parameters within the url
@app.route('/<focus>/<name>/<img>/<ability>/<type>')
#define function for pokedex that takes the following inputs
def pokedex(focus,name,img,ability,type):
    #if focus is empty then nothing will be displayed apart from the list of pokemon
    if focus == '':
        #render html template with focus as false
        return render_template("index.html", list=dict,focus=False)
    #else if focus is not empty then png will be set to an image of the specific pokemon requested
    else:
        png = f'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{img}.png'
        #return the template with focus=true which will end up returning a "card" of the pokemon containing the pokemon name, image, ability, and type
        return render_template("index.html", list=dict, focus=True, name=name,img=png,ability=ability,type=type)

#create a search function using post
@app.route("/search", methods=["POST"])
def search():
    try:
        #set the name of the pokemon as what the user inputs within the searchbar
        pokemon_name= request.form.get("pokemon_search")
        #obtain the json content about the pokemon searched
        r = requests.get('https://pokeapi.co/api/v2/pokemon/' + pokemon_name).json()
        #obtain the information about the pokemon
            #to understand what to set ability to, go into the json content regarding the pokemon and find how ability is accessed
            #accessed within "abilities" and the ability is the name of the first term within ability name
        ability = r['abilities'][0]['ability']['name']
        #repeat process used to obtain ability for type, id of the pokemon, and the number of the pokemon
        type = r['types'][0]['type']['name']
        id = r['types'][0]['type']['name']
        nr = str(r['id']).zfill(3)
        #set png again to the image of the searched pokemon's number
        png = f'https://assets.pokemon.com/assets/cms2/img/pokedex/full/{nr}.png'
        #return the template this time with focus being true and therefore showing the "card" of the pokemon upon search which will display the name, image, ability, and type of the searched pokemon
        return render_template("index.html", list=dict, focus=True, name=r['name'], img=png, ability=ability, type=type)
    except ValueError:
        print("That is not a pokemon!")
        return render_template("error.html")
    #used try, except function to tell the user within the terminal that the value they inputted was not a pokemon

#make an app.route for the card to show up when one of the pokemon within the list are clicked
@app.route('/card/<focus>')
#make the function pokemon_card take the focus from the clicked image
def pokemon_card(focus):
    #get the json content from the link using the focus from the clicked image
    r = requests.get('https://pokeapi.co/api/v2/pokemon/' + focus).json()
    #repeat process used in search
    ability = r['abilities'][0]['ability']['name']
    type = r['types'][0]['type']['name']
    nr = str(r['id']).zfill(3)
    #use redirect to redirect the url for pokedex to have focus as true and contain the information of the pokemon clicked on the left side of the screen, this will allow for the information about the pokemon to be displayed as the url is redirected to show the card of the pokemon clicked
    return redirect(url_for('pokedex', focus=True, ability=ability, name=r['name'], img=nr, type=type))

if __name__ == "__main__":
  app.run()
