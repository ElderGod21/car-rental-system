from fastapi import APIRouter, HTTPException
from models.car_rental_models import Car, CarRental
from database.config import client
from database.rules import Rules
from bson import ObjectId
import os

router = APIRouter()

@router.post('/cars')
async def add_car(car: Car):
    try:
        cars = dict(car)
        cars['_id'] = ObjectId()
        exsisting_cars = Rules.get_all(client, os.getenv('DB_NAME'), 'cars', {})
        if exsisting_cars:
            cars['car_id'] = exsisting_cars[-1]['car_id'] + 1
        else:
            cars['car_id'] = 1
        operation_id = Rules.add(client, os.getenv('DB_NAME'), 'cars', cars)
        return {'status_code': 200, 'message': 'Car added successfully', 'operation_id': str(operation_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/cars')
async def get_cars():
    try:
        cars = Rules.get_all(client, os.getenv('DB_NAME'), 'cars', {})
        for car in cars:
            car['_id'] = str(car['_id'])
        return {'status_code': 200, 'message': 'Cars fetched successfully', 'cars': cars}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/cars/{car_id}')
async def get_car(car_id: int):
    try:
        car = Rules.get(client, os.getenv('DB_NAME'), 'cars', {'car_id': car_id})
        if not car:
            raise HTTPException(status_code=404, detail='Car not found')
        car['_id'] = str(car['_id'])
        return {'status_code': 200, 'message': 'Car fetched successfully', 'car': car}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/cars/{car_id}/rent')
async def rent_car(car_id: int, rental: CarRental):
    try:
        car = Rules.get(client, os.getenv('DB_NAME'), 'cars', {'car_id': car_id})
        if not car:
            raise HTTPException(status_code=404, detail='Car not found')
        else:
            if rental.end_date < rental.start_date:
                raise HTTPException(status_code=400, detail='End date must be greater than start date')
            else:
                exsisting_rentals = Rules.get_all(client, os.getenv('DB_NAME'), 'rentals', {'car_id': car_id})
                if exsisting_rentals:
                    latest_rental = sorted(exsisting_rentals, key=lambda x: x['rental_date'], reverse=True)[0]
                    if latest_rental['start_date'] <= rental.start_date <= latest_rental['end_date']:
                        if latest_rental['start_date'] <= rental.end_date <= latest_rental['end_date']:
                            raise HTTPException(status_code=400, detail='Car is already rented at the time of your request')
                        else:
                            return {'status_code': 400, 'message': 'Car is already rented at the time of your start date', 'available_from': latest_rental['end_date']}
                    else:
                        if latest_rental['start_date'] <= rental.end_date <= latest_rental['end_date']:
                            return {'status_code': 400, 'message': 'Car is already rented at the time of your request', 'available_till': latest_rental['start_date']}
                        else:
                            rentals = dict(rental)
                            exsisting_rentals = Rules.get_all(client, os.getenv('DB_NAME'), 'rentals', {})
                            rentals['rental_id'] = len(exsisting_rentals) + 1
                            car['available'] = False
                            Rules.update(client, os.getenv('DB_NAME'), 'cars', {'car_id': car_id}, car)
                            rentals['car_id'] = car_id
                            operation_id = Rules.add(client, os.getenv('DB_NAME'), 'rentals', rentals)
                            return {'status_code': 200, 'message': 'Car rented successfully', 'operation_id': str(operation_id)}
                else:
                    if car['available'] == False:
                        raise HTTPException(status_code=400, detail='Car is not available')
                    else:
                        rentals = dict(rental)
                        exsisting_rentals = Rules.get_all(client, os.getenv('DB_NAME'), 'rentals', {})
                        rentals['rental_id'] = len(exsisting_rentals) + 1
                        car['available'] = False
                        Rules.update(client, os.getenv('DB_NAME'), 'cars', {'car_id': car_id}, car)
                        rentals['car_id'] = car_id
                        operation_id = Rules.add(client, os.getenv('DB_NAME'), 'rentals', rentals)
                        return {'status_code': 200, 'message': 'Car rented successfully', 'operation_id': str(operation_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/rentals/{rental_id}')
async def delete_rental(rental_id: int):
    try:
        rental = Rules.get(client, os.getenv('DB_NAME'), 'rentals', {'rental_id': rental_id})
        if not rental:
            raise HTTPException(status_code=404, detail='Rental not found')
        else:
            car = Rules.get(client, os.getenv('DB_NAME'), 'cars', {'car_id': rental['car_id']})
            car['available'] = True
            Rules.update(client, os.getenv('DB_NAME'), 'cars', {'car_id': rental['car_id']}, car)
            Rules.delete(client, os.getenv('DB_NAME'), 'rentals', {'rental_id': rental_id})
            return {'status_code': 200, 'message': 'Rental deleted successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))