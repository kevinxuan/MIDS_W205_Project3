#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')


SWORD_TYPE_TO_PRICE = {
    'gold': 15,
    'silver': 10,
    'bronze': 5
}

def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())


@app.route("/")
def default_response():
    default_event = {'event_type': 'default'}
    log_to_kafka('events', default_event)
    return "This is the default response!\n"


@app.route("/purchase_a_sword")
def purchase_a_sword():
    user = request.args.get('user')
    sword_type = request.args.get('type')
    price = SWORD_TYPE_TO_PRICE.get(sword_type, 0)
    purchase_sword_event = {'event_type': 'purchase_sword', 'user': user, 'price': price, 'type': sword_type}
    log_to_kafka('events', purchase_sword_event)
    return "Sword Purchased!\n"


@app.route("/join_a_guild")
def join_a_guild():
    user = request.args.get('user')
    guild_name = request.args.get('name')
    join_guild_event = {'event_type': 'join_a_guild', 'user': user, 'fee': 5, 'name': guild_name}
    log_to_kafka('events', join_guild_event)
    return "Guild Joined!\n"


@app.route("/quit_guild")
def quit_guild():
    user = request.args.get('user')
    guild_name = request.args.get('name')
    quit_guild_event = {'event_type': 'quit_guild', 'user': user, 'name': guild_name}
    log_to_kafka('events', quit_guild_event)
    return "Guild Quitted.\n"


@app.route("/get_paid")
def get_paid():
    user = request.args.get('user')
    amount = request.args.get('amount')
    get_paid_event = {'event_type': 'get_paid', 'user': user, 'amount': float(amount)}
    log_to_kafka('events', get_paid_event)
    return "Just got paid!\n"
