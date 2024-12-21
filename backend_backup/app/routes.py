import datetime
import pandas
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status

from utils import *
from schemas import *
from helpers import get_db, Queue, get_channels
from datetime import datetime, timedelta


router = APIRouter()



@ router.get(path='/device', tags=[""], response_model=DeviceList)
def get_device_list(offset_limit=Depends(get_offset_limit), db=Depends(get_db)):

    
    records, length = [], 0
    data = records, length
    return get_pages_records(data, offset_limit)



@ router.delete(path='/device', tags=[""])
def delete_device(id: UUID, db=Depends(get_db)):

    return "OK"

def calculate_cost(self):
    return calculate_cost(self.usage_kwh)

def get_energy_data(start_date=None, end_date=None, db=None):
    def timestamp_to_date(ts):
        return datetime.datetime.fromtimestamp(ts / 1000).date()

    if start_date is None and end_date is None:
        return sum(entry["energy"] for entry in energy_data)
    
    filtered_data = [
        entry for entry in energy_data 
        if start_date <= timestamp_to_date(entry["ts"]) <= end_date
    ]
    return sum(entry["energy"] for entry in filtered_data)



@router.get(path='/device/energy/today', tags=["Energy"],)
def get_today_energy_cost(db=Depends(get_db)):
    today = datetime.now().date()
    energy_consumed = get_energy_data(today, today, db)
    cost = calculate_cost(energy_consumed)
    return {"energy_consumed": energy_consumed, "cost": cost,}


@router.get(path='/device/energy/month', tags=["Energy"],)
def get_month_energy_cost(db=Depends(get_db)):
    today = datetime.now()
    start_of_month = today.replace(day=1)
    energy_consumed = get_energy_data(start_of_month, today, db)
    cost = calculate_cost(energy_consumed)
    return {"energy_consumed": energy_consumed, "cost": cost}


@router.get(path='/device/energy/year', tags=["Energy"],)
def get_year_energy_cost(db=Depends(get_db)):
    today = datetime.now()
    start_of_year = today.replace(month=1, day=1)
    energy_consumed = get_energy_data(start_of_year, today, db)
    cost = calculate_cost(energy_consumed)
    return {"energy_consumed": energy_consumed, "cost": cost}


@router.get(path='/device/energy/total', tags=["Energy"],)
def get_total_energy_cost(db=Depends(get_db)):
    energy_consumed = get_energy_data(None, None, db)  
    cost = calculate_cost(energy_consumed)
    return {"energy_consumed": energy_consumed, "cost": cost}


@ router.delete(path='/device', tags=[""])
def delete_device(id: UUID, db=Depends(get_db)):

    return "OK"

energy_data = [
    {"ts": 1732801051000, "energy": 100},
    {"ts": 1732887451000, "energy": 120},
    {"ts": 1732973851000, "energy": 150},
    {"ts": 1733060251000, "energy": 180},
    {"ts": 1733146651000, "energy": 200},
]

class BillRequest(BaseModel):
    ts: int  
    usage_kwh: float

def convert_epoch_to_date(ts: int):
    date = datetime.fromtimestamp(ts / 1000)
    return date.day, date.month, date.year, date.strftime("%d/%m/%Y")

@router.post(path='/device/bill', tags=["Bill"])
def get_electricity_bill(bill_request: BillRequest):
    day, month, year, formatted_date = convert_epoch_to_date(bill_request.ts)
    bill = ElectricityBill(
        day=day,
        month=month,
        year=year,
        usage_kwh=bill_request.usage_kwh
    )
    total_cost = bill.calculate_bill()
    
    return {
        "date": formatted_date,
        "usage_kwh": bill.usage_kwh,
        "total_cost": f"{total_cost:,} VNĐ"
    }

class ElectricityBill:
    def __init__(self, day, month, year, usage_kwh):
        self.day = day
        self.month = month
        self.year = year
        self.usage_kwh = usage_kwh
        self.rates = {
            "Mức 1": (0, 50, 1894),
            "Mức 2": (51, 100, 1956),
            "Mức 3": (101, 200, 2271),
            "Mức 4": (201, 300, 2860),
            "Mức 5": (301, 400, 3197),
            "Mức 6": (401, float('inf'), 3302)
        }

    def calculate_bill(self):
        total_amount = 0
        remaining_kwh = self.usage_kwh
        
        for level, (min_kwh, max_kwh, rate) in self.rates.items():
            if remaining_kwh <= 0:
                break
            
            if min_kwh == 0:
                current_usage = min(remaining_kwh, max_kwh)
            else:
                current_usage = min(remaining_kwh, max_kwh - min_kwh + 1)
                
            total_amount += current_usage * rate
            remaining_kwh -= current_usage
        
        return total_amount

    def display_bill(self):
        total_amount = self.calculate_bill()
        print(f"Ngày: {self.day}/{self.month}/{self.year}")
        print(f"Số điện sử dụng: {self.usage_kwh} kWh")
        print(f"Tổng tiền điện: {total_amount:,} VNĐ")


# Ví dụ sử dụng
bill = ElectricityBill(day=29, month=11, year=2024, usage_kwh=250)
bill.display_bill()

def calculate_energy_cost(daily_consumption_kwh, price_per_kwh):
    today = datetime.today()
    days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).day
    days_in_year = 365

    # Tính tiêu thụ và chi phí
    daily_cost = daily_consumption_kwh * price_per_kwh
    monthly_consumption = daily_consumption_kwh * days_in_month
    yearly_consumption = daily_consumption_kwh * days_in_year

    monthly_cost = monthly_consumption * price_per_kwh
    yearly_cost = yearly_consumption * price_per_kwh

    total_energy = yearly_consumption

    print(f"Daily Cost: {daily_cost:.3f} VND")
    print(f"Monthly Consumption: {monthly_consumption:.3f} kWh, Cost: {monthly_cost:.3f} VND")
    print(f"Yearly Consumption: {yearly_consumption:.3f} kWh, Cost: {yearly_cost:.3f} VND")
    print(f"Total Energy Consumption (Yearly): {total_energy:.3f} kWh")

# Ví dụ sử dụng:
daily_consumption_kwh = 5  
price_per_kwh = 3000  

calculate_energy_cost(5, 3000)