# Roadtrip!

[![Build Status](https://travis-ci.com/iandouglas/udacity-fsnd-capstone.svg?branch=master)](https://travis-ci.com/iandouglas/udacity-fsnd-capstone)

Who doesn't love a road trip? Besides my wife. And my dog who gets carsick.
And my children who would rather be playing Minecraft.

Let's build an API for creating and modifying road trip information which
calls on OpenWeather and MapQuest to fetch forecast data at our destination
city right now, and build a road trip which will also project the forecast
when we arrive.

## Project Requirements

### General Specifications

Models will include at least:
- Two classes with primary keys at at least two attributes each
  - user class only has username and id
  - city class has city, state, latitude and longitude, and id
  - roadtrip class has name,and relationships to users and cities
- Optional but encouraged: One-to-many or many-to-many relationships between 
  classes
  - this project includes both a one-to-many (one user can have many road 
  trips) and a many-to-many (technically, a user has many cities through the
  road trips table, making it a 'join' table between users and cities)

Endpoints will include at least:
- Two GET requests
  - GET /api/forecast?city=Arvada,CO
  - GET /api/roadtrips
  - GET /api/cities
  - GET /api/roadtrips/1
- One POST request
  - POST /api/roadtrips
- One PATCH request
  - PATCH /api/roadtrips/1
- One DELETE request
  - DELETE /api/roadtrips/1

Roles will include at least:
- Two roles with different permissions
  - role 1: unauthenticated user
    - user will be able to log in
    - user can fetch forecast data
  - role 2: authenticated user
    - "get:roadtrips"
    - "create:roadtrips"
    - "update:roadtrips"
    - "delete:roadtrips"
- Permissions specified for all endpoints
  - home page and callback cannot have permissions, obviously
  - forecast endpoint will not have permissions to allow for anonymous users
  - all other CRUD endpoints will have permissions set

Tests will include at least:
- One test for success behavior of each endpoint
- One test for error behavior of each endpoint
- At least two tests of RBAC for each role

Uh, yeah, pretty sure I have test coverage for all that :)

## Endpoints

- GET and PATCH endpoints will return a 200 status code on success
- POST endpoints will return a 201 status code on success
- DELETE endpoints will return a 204 status code on success

Failure conditions will return an appropriate 400-series or 500-series error
and a JSON payload indicating helpful errors in a format such as:
```json
{
  "error": 404,
  "message": "Resource not found"
}
```

#### GET /api/forecast?city=Arvada,CO

Description:
- fetches current weather in Arvada, CO from OpenWeather

Required Request Headers:
- none

Required Auth Role:
- none

Required Request Body:
- none

Response Body: (TBD)
```json
{
  "location": "Arvada, CO",
  "current_temp": "79.3F",
  "conditions": "partly cloudy"
}
```

#### GET /api/roadtrips

Description:
- fetches all road trips for authenticated user

Required Request Headers:
- TBD

Required Auth Role:
- "get:roadtrips"

Required Request Body:
- none

Response Body: (TBD)
```json
[
  {
    "starting_city": "Denver, CO",
    "ending_city": "Estes Park, CO"
  },
  {
    "starting_city": "Arvada, CO",
    "ending_city": "Denver, CO"
  },
  {...}
]
```

#### GET /api/cities

Description:
- fetches quantities of road trips by city

Required Request Headers:
- TBD

Required Auth Role:
- "get:roadtrips"

Required Request Body:
- none

Response Body: (TBD)
```json
{
  "starting_cities": {
    "Arvada, CO": 2,
    "Denver, CO": 3
  },
  "ending_cities": {
    "Arvada, CO": 2,
    "Estes Park, CO": 2,
    "Denver, CO": 1,
  }
}
```

#### GET /api/roadtrips/1

Description:
- fetches information about road trip #1 in our database

Required Request Headers:
- TBD

Required Auth Role:
- "get:roadtrips"

Required Request Body:
- none

Response Body: (TBD)
```json
{
  "starting_city": "Denver, CO",
  "ending_city": "Estes Park, CO",
  "travel_time": "2 hours, 13 minutes",
  "forecast_at_eta": {
    "temp": "52.5F",
    "conditions": "mostly cloudy"
  }
}
```

#### POST /api/roadtrips

Description:
- creates a road trip between two cities

Required Request Headers:
- TBD

Required Auth Role:
- "create:roadtrips"

Required Request Body:
- JSON payload of 'start_city', 'end_city'
```json
{
  "start_city": "Arvada, CO",
  "end_city": "Estes Park, CO"
}
```

Response Body: (TBD)
- json payload indicating road trip was created, including a restful route
  to fetch road trip information


#### PATCH /api/roadtrips/1

Description:
- updates a road trip by ID between two cities

Required Request Headers:
- TBD

Required Auth Role:
- "update:roadtrips"

Required Request Body:
- JSON payload of 'start_city', 'end_city'
- payload can include one or the other, or both
```json
{
  "start_city": "Arvada, CO",
  "end_city": "Estes Park, CO"
}
```

Response Body: (TBD)
- json payload indicating road trip was updated, including a restful route
  to fetch road trip information


#### DELETE /api/roadtrips/1

Description:
- deletes a road trip by ID

Required Request Headers:
- TBD

Required Auth Role:
- "delete:roadtrips"

Required Request Body:
- none

Response Body: (TBD)
- none on success

