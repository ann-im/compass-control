import asyncio
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from boxbot import BoxBot, AckermannBot
from boxbot import PIDController
from viam.robot.client import RobotClient
from viam.components.movement_sensor import MovementSensor

# PID parameters
kp_heading = 0.004  # Proportional gain
ki_heading = 0.0005 # Integral gain
kd_heading = 0.001  # Derivative gain

kp_target = 0.004   # Proportional gain
ki_target = 0.000   # Integral gain
kd_target = 0.000   # Derivative gain

kp_linear = 0.002  # Proportional gain
ki_linear = 0.002  # Integral gain
kd_linear = 0.000 # Derivative gain

# Integral term saturation limits
integral_max_heading = 150  # Adjust as needed
integral_min_heading = -150  # Adjust as needed

integral_max_target = 150  # Adjust as needed
integral_min_target = -150  # Adjust as needed

integral_max_linear = 150  # Adjust as needed
integral_min_linear = 0  # Adjust as needed

async def connect():
    # Load environment variables
    load_dotenv()
    
    api_key = os.environ.get('ENV_API_KEY')
    api_key_id = os.environ.get('ENV_API_KEY_ID')
    host = os.environ.get('ENV_HOST')
    
    opts = RobotClient.Options.with_api_key(
        api_key=api_key,
        api_key_id=api_key_id
    )
    return await RobotClient.at_address(host, opts)

def extract_coordinates_from_csv(file_path):
    """
    Reads a CSV file with columns: timestamp, latitude, longitude, altitude.
    Extracts the latitude and longitude points and returns them in an array
    where each element is an array containing a pair of coordinates.

    Args:
    file_path (str): The path to the CSV file.

    Returns:
    list of lists: A list of [latitude, longitude] pairs.
    """
    coordinates = []

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        for row in csv_reader:
            if len(row) >= 3:
                latitude = float(row[1])
                longitude = float(row[2])
                coordinates.append([latitude, longitude])

    return coordinates

async def main():
    coord_log = []
    current_time = datetime.now().strftime("%Y%m%d_%H-%M-%S")
    log_file_name = f'logs/gpsNavLog_{current_time}.csv'
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True)

    robot = await connect()
    sensor_motion = MovementSensor.from_robot(robot, "gpsRight")
    sensor_gps_right = MovementSensor.from_robot(robot, "gpsRight")
    sensor_gps_left = MovementSensor.from_robot(robot, "gpsLeft")

    replay_file = os.environ.get('ENV_FILEPATH')
    GPSarray = extract_coordinates_from_csv(replay_file)

    with open(log_file_name, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        ackermann_bot = AckermannBot(robot, csv_writer)

        for coords in GPSarray:
            print(f"Going to {coords[0]}, {coords[1]}")
            await ackermann_bot.navigate(ackermann_bot, sensor_motion, sensor_gps_right, sensor_gps_left, coords[0], coords[1], coord_log)



if __name__ == '__main__':
    asyncio.run(main())
