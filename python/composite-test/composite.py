#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import random
import logging
import cgi
import datetime
import webapp2

from google.appengine.ext  import db
from google.appengine.api import users
import time

class Cars(db.Model):
  model = db.StringProperty(required=True)
  make = db.StringProperty(required=True)
  color = db.StringProperty(required=True)
  value = db.IntegerProperty(required=True)

class MainPage(webapp2.RequestHandler):
  """ Queries that use a set of equality filters use the zigzag merge join 
  algorithm.
  """
  def get(self):
    non_set_cars = []
    for x in range(0, 10):
      model = random.choice(["SModel", "Civic", "S2000"])
      make = random.choice(["Tesla", "Ford"])
      # The color will never match what we are querying for.
      color = random.choice(["red", "green", "blue"])
      value = x
      car = Cars(model=model, make=make, color=color, value=value)
      
      non_set_cars.append(car)
    db.put(non_set_cars)

    set_cars = []
    for x in range(0, 10):
      car = Cars(model="SModel", make="Tesla", color="purple", value=x)
      set_cars.append(car)
    db.put(set_cars)

    second_set = []
    for x in range(0, 10):
      car = Cars(model="Camry", make="Toyota", color="gold", value=x)
      second_set.append(car)
    db.put(second_set)

    q = Cars.all()
    q.filter("model =", "SModel")
    q.filter("make =", "Tesla")
    q.filter("color =", "purple")
    q.filter("value >", 4)  
    q.filter("value <", 6)  
    results = q.fetch(100)

    q = Cars.all()
    q.filter("model =", "SModel")
    q.filter("make =", "Tesla")
    q.filter("color =", "purple")
    q.filter("value >=", 4)  
    q.filter("value <=", 6)  
    results_2 = q.fetch(100)

    q = Cars.all()
    q.filter("model =", "Camry")
    q.filter("make =", "Toyota")
    q.filter("color =", "gold")
    q.filter("value >", 4)  
    q.filter("value <=", 6)  
    results_3 = q.fetch(100)

    q = Cars.all()
    q.filter("model =", "Camry")
    q.filter("make =", "Toyota")
    q.filter("color =", "gold")
    q.filter("value >=", 4)  
    q.filter("value <", 6)  
    results_4 = q.fetch(100)


    db.delete(non_set_cars)
    db.delete(set_cars)
    db.delete(second_set)

    if len(results) != 1:
      logging.error("Result for query was {0}, expected 1 item".format(results))
      for result in results:
        logging.info("Item: {0}".format(result.value))
      self.response.set_status(404)
    elif len(results_2) != 3:
      logging.error("Result for query was {0}, expected 3 items".format(results_2))
      self.response.set_status(404)
    elif len(results_3) != 2:
      logging.error("Result for query was {0}, expected 2 items".format(results_3))
      self.response.set_status(404)
    elif len(results_4) != 2:
      logging.error("Result for query was {0}, expected 2 items".format(results_4))
      self.response.set_status(404)
    else:
      self.response.set_status(200)

app = webapp2.WSGIApplication([
  ('/', MainPage),
], debug=True)
