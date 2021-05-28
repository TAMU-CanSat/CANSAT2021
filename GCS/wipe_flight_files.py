import time

def wipe_and_archive():
    TEAM_ID = 2743

    # The datafiles directory should be under this directory
    ROOT_DIRECTORY = ""

    filename_cansat = ROOT_DIRECTORY + "datafiles/Flight_" + str(TEAM_ID) + "_C"
    filename_sp1 = ROOT_DIRECTORY + "datafiles/Flight_" + str(TEAM_ID) + "_SP1"
    filename_sp2 = ROOT_DIRECTORY + "datafiles/Flight_" + str(TEAM_ID) + "_SP2"


    # Get the current date and time
    dateTimeString = time.strftime("%Y%m%d-%H-%M-%S") + "--"

    # Set filenames for archive files
    filename_archive_cansat = ROOT_DIRECTORY + "datafiles/archive/" + dateTimeString + "Flight_" + str(TEAM_ID) + "_C"
    filename_archive_sp1 = ROOT_DIRECTORY + "datafiles/archive/" + dateTimeString + "Flight_" + str(TEAM_ID) + "_SP1"
    filename_archive_sp2 = ROOT_DIRECTORY + "datafiles/archive/" + dateTimeString + "Flight_" + str(TEAM_ID) + "_SP2"

    # Create new archival files and write to them
    archive_cansat = open(filename_archive_cansat + ".csv", 'w')
    archive_sp1 = open(filename_archive_sp1 + ".csv", 'w')
    archive_sp2 = open(filename_archive_sp2 + ".csv", 'w')

    # Read in telemetry, write to archive files
    telemetry_cansat = open(filename_cansat + ".csv", 'r')
    telemetry_sp1 = open(filename_sp1 + ".csv", 'r')
    telemetry_sp2 = open(filename_sp2 + ".csv", 'r')

    for line in telemetry_cansat:
        archive_cansat.write(line)

    for line in telemetry_sp1:
        archive_sp1.write(line)

    for line in telemetry_sp2:
        archive_sp2.write(line)

    # Close all files
    telemetry_cansat.close()
    telemetry_sp1.close()
    telemetry_sp2.close()
    archive_cansat.close()
    archive_sp1.close()
    archive_sp2.close()

    # Wipe telemetry files
    telemetry_cansat = open(filename_cansat + ".csv", 'w')
    telemetry_sp1 = open(filename_sp1 + ".csv", 'w')
    telemetry_sp2 = open(filename_sp2 + ".csv", 'w')

    # Close the files
    telemetry_cansat.close()
    telemetry_sp1.close()
    telemetry_sp2.close()

    print("Flight datafiles have been archived")
    print("New flight datafiles have been created\n")
