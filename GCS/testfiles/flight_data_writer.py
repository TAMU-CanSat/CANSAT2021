# Purpose: Copy data from Dummy csv files to Flight csv files to imitate an actual flight for GUI testing

# Imports
import time

# Configuration items
TEAM_ID = 2992

# The datafiles directory should be under this directory
ROOT_DIRECTORY = "../"


def write_data(teamid, quick, delay):
    global ROOT_DIRECTORY

    # Open telemetry files for writing to clear them
    telemetry_cansat = open(ROOT_DIRECTORY + "datafiles/Flight_" + str(teamid) + "_C.csv", 'w')
    telemetry_sp1 = open(ROOT_DIRECTORY + "datafiles/Flight_" + str(teamid) + "_SP1.csv", 'w')
    telemetry_sp2 = open(ROOT_DIRECTORY + "datafiles/Flight_" + str(teamid) + "_SP2.csv", 'w')

    # Close the files
    telemetry_cansat.close()
    telemetry_sp1.close()
    telemetry_sp2.close()

    # Count the number of lines in datafile_cansat to provide a readout on the console
    datafile_cansat = open(ROOT_DIRECTORY + "datafiles/Dummy_" + str(teamid) + "_C.csv", 'r')
    lines = -1
    lines_processed = 0
    for line in datafile_cansat:
        lines += 1
    datafile_cansat.close()

    # Implement delay
    if delay != 0:
        time.sleep(delay)

    # Open data(dummy) files for reading
    datafile_cansat = open(ROOT_DIRECTORY + "datafiles/Dummy_" + str(teamid) + "_C.csv", 'r')
    datafile_sp1 = open(ROOT_DIRECTORY + "datafiles/Dummy_" + str(teamid) + "_SP1.csv", 'r')
    datafile_sp2 = open(ROOT_DIRECTORY + "datafiles/Dummy_" + str(teamid) + "_SP2.csv", 'r')

    # Dump the headers from each datafile (They wouldn't be present in the competition csv)
    datafile_cansat.readline()
    datafile_sp1.readline()
    datafile_sp2.readline()

    # Setup variables to start payload packet writing
    sp1 = False
    sp2 = False

    # Begin writing to the telemetry files
    for cansat_line in datafile_cansat:
        # Open the telemetry files
        telemetry_cansat = open(ROOT_DIRECTORY + "datafiles/Flight_" + str(teamid) + "_C.csv", 'a')
        telemetry_sp1 = open(ROOT_DIRECTORY + "datafiles/Flight_" + str(teamid) + "_SP1.csv", 'a')
        telemetry_sp2 = open(ROOT_DIRECTORY + "datafiles/Flight_" + str(teamid) + "_SP2.csv", 'a')

        # Write the cansat line to the datafile for the cansat
        telemetry_cansat.write(cansat_line)
        telemetry_cansat.close()

        # Check for payload release to write payload files
        if sp1 or "SP1XON" in cansat_line:
            sp1 = True
            telemetry_sp1.write(datafile_sp1.readline())

        if sp2 or "SP2XON" in cansat_line:
            sp2 = True
            telemetry_sp2.write(datafile_sp2.readline())

        # Close the files
        telemetry_cansat.close()
        telemetry_sp1.close()
        telemetry_sp2.close()

        # Display remaining lines
        lines_processed += 1
        print("Lines processed/total: {}/{}".format(lines_processed, lines))

        # Sleep for a second to simulate 1Hz transmission rate
        if not quick:
            time.sleep(1)


# Mode select
print("Mode select:")
print("1. Quick write")
print("2. Loop forever (5 second delay)")
print("3. Delayed start (5 second delay)")
print("Enter your choice: ", end="")
choice = int(input())

if choice == 1:
    write_data(TEAM_ID, True, 0)
elif choice == 2:
    while True:
        write_data(TEAM_ID, False, 5)
elif choice == 3:
    write_data(TEAM_ID, False, 5)
else:
    print("Choice UNKNOWN, please try again")
