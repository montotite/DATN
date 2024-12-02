import datetime
import pandas
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status

from utils import *
from schemas import *
from helpers import get_db, Queue, get_channels


router = APIRouter()



@ router.get(path='/device', tags=[""], response_model=DeviceList)
def get_device_list(offset_limit=Depends(get_offset_limit), db=Depends(get_db)):

    
    records, length = [], 0
    data = records, length
    return get_pages_records(data, offset_limit)


@ router.post(path='/device', tags=[""], response_model=DeviceInfo)
def create_device(form_data: DeviceInfo,
                  db=Depends(get_db)):

    device_id = ""
    return get_device_info(device_id, db)


@ router.get(path='/device/info', tags=[""], response_model=DeviceInfo)
def get_device_info(id: UUID, db=Depends(get_db)):
    return 



@ router.delete(path='/device', tags=[""])
def delete_device(id: UUID, db=Depends(get_db)):

    return "OK"


@router.get(path='/device/energy/today', tags=["Energy"],)
def get_today_energy_cost(db=Depends(get_db)):
    today = datetime.now().date()
    energy_consumed = get_energy_data(today, today, db)
    cost = calculate_cost(energy_consumed)
    return {"energy_consumed": energy_consumed, "cost": cost}


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
    energy_consumed = get_energy_data(None, None, db)  # None -> lấy toàn bộ dữ liệu
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



# Hàm lấy dữ liệu cho từng cột và chuyển đổi ngày thành Epoch
def get_energy_column_with_epoch(data, column_index):
    entry = data[column_index]
    epoch_time = convert_to_epoch(entry["day"])
    return {"epoch_time": epoch_time, "energy": entry["energy"]}



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
bill = ElectricityBill(day=29, month=11, year=2024, usage_kwh=350)
bill.display_bill()
