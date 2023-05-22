library (gtfsrouter)
packageVersion ("gtfsrouter")
library(lubridate)
library('plyr')
library('dplyr')
library('stringr')
library('pbapply')

# 

url <- "https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip"
f <- "gtfs_stm.zip"
if (!file.exists (f)) download.file (url, destfile = f)

gtfs <- extract_gtfs (f)

gtfs <- gtfs_transfer_table (gtfs, d_limit = 200)

gtfs <- gtfs_timetable (gtfs, day = "Wednesday")
#gtfs <- gtfs_timetable (gtfs, date = 20230524)

outDir<-"tmp_data"
unzip(f,exdir=outDir)

stops <- read.csv("tmp_data/stops.txt")

for (stop_id in stops$stop_id) {
    print(paste0('Processing data for stop ', stop_id))
    x <- gtfs_traveltimes (
        gtfs,
        from = stop_id,
        from_is_id = TRUE,
        start_time_limits = c (12, 14) * 3600,
        max_traveltime = 60 * 60 * 4,
    )
    x$duration <- period_to_seconds(hms(x$duration))
    write.csv(x, paste0("/Users/bmorris/github/gmt-isochrones/data/durations/",stop_id, ".csv"), row.names=FALSE)
}
